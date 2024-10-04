#!/usr/bin/python3
from __future__ import annotations

import json
import os.path
import site
import subprocess
import tarfile
import urllib.request
from dataclasses import dataclass
from tempfile import TemporaryDirectory


@dataclass
class Release:
    name: str
    slug: str
    version: int
    is_published: bool
    is_latest: bool
    release_date: str
    pre_release: bool
    release_page: None
    release_notes_url: str
    show_on_download_page: bool
    resource_uri: str


@dataclass
class ReleaseFile:
    name: str
    slug: str
    os: str
    release: str
    description: str
    is_source: bool
    url: str
    gpg_signature_file: str
    md5_sum: str
    filesize: int
    download_button: bool
    resource_uri: str
    sigstore_signature_file: str
    sigstore_cert_file: str
    sigstore_bundle_file: str
    sbom_spdx2_file: str


@dataclass
class ReleaseCycle:
    branch: str
    pep: int
    status: str
    first_release: str
    end_of_life: str
    release_manager: str


RELEASE_LIST_URL = "https://www.python.org/api/v2/downloads/release/"
RELEASE_FILE_LIST_URL = "https://www.python.org/api/v2/downloads/release_file/"
RELEASE_CYCLE_URL = (
    "https://github.com/python/devguide/raw/main/include/release-cycle.json"
)


def fetch_release_list() -> list[Release]:
    with urllib.request.urlopen(RELEASE_LIST_URL) as response:
        content = json.load(response)
    assert isinstance(content, list)
    return [Release(**release) for release in content]


def fetch_release_file_list() -> list[ReleaseFile]:
    with urllib.request.urlopen(RELEASE_FILE_LIST_URL) as response:
        content = json.load(response)
    assert isinstance(content, list)
    return [ReleaseFile(**release_file) for release_file in content]


def fetch_release_cycle() -> dict[str, ReleaseCycle]:
    with urllib.request.urlopen(RELEASE_CYCLE_URL) as response:
        content = json.load(response)
    assert isinstance(content, dict)
    return {k: ReleaseCycle(**v) for k, v in content.items()}


def main() -> None:
    # Retrive active minor releases
    release_cycle = fetch_release_cycle()

    active_minor_release: list[tuple[int, int]] = []
    for key, cycle in release_cycle.items():
        if cycle.status != "end-of-life":
            minor_parts = key.split(".")
            assert len(minor_parts) == 2
            minor_tuple = (int(minor_parts[0]), int(minor_parts[1]))
            active_minor_release.append(minor_tuple)

    # Retrive latest releases
    release_list = fetch_release_list()
    latest_minor_release: dict[tuple[int, int], Release] = {}
    for release in release_list:
        version_parts = release.name.removeprefix("Python ").split(".")
        assert len(version_parts) == 3
        minor_tuple = (int(version_parts[0]), int(version_parts[1]))

        if minor_tuple not in active_minor_release:
            continue

        # latest release
        if minor_tuple not in latest_minor_release:
            latest_minor_release[minor_tuple] = release
        elif release.release_date > latest_minor_release[minor_tuple].release_date:
            latest_minor_release[minor_tuple] = release

    # print(*sorted(latest_minor_release.items()), sep="\n")
    latest_minor_release = dict(sorted(latest_minor_release.items()))

    # Retrive latest minor release files
    release_file_list = fetch_release_file_list()
    latest_minor_release_file: dict[tuple[int, int], str] = {}
    for minor_tuple, release in latest_minor_release.items():
        release_file = next(
            filter(
                lambda x: x.release == release.resource_uri
                and x.name == "Gzipped source tarball",
                release_file_list,
            ),
            None,
        )
        if release_file is not None:
            latest_minor_release_file[minor_tuple] = release_file.url

    # print(latest_minor_release_file)

    # Get user Python
    for minor_tuple, release in latest_minor_release.items():
        assert site.USER_BASE is not None
        user_minor_executable = os.path.join(
            site.USER_BASE, "bin", "python" + ".".join(map(str, minor_tuple))
        )
        print(f"{user_minor_executable=:} {os.path.exists(user_minor_executable)=:}")

        # Check
        if os.path.exists(user_minor_executable):
            ret = subprocess.run(
                [user_minor_executable, "-V"],
                capture_output=True,
                check=True,
                text=True,
            )

            if ret.stdout.strip() == release.name:
                print(f"Python {release.name} is already installed.")
                continue
            else:
                print(f"Python {release.name} is not updated.")
        else:
            print(f"Python {release.name} is not installed.")

        # Install
        with TemporaryDirectory() as temp_dir:
            download_url = latest_minor_release_file[minor_tuple]
            basename = os.path.basename(download_url)
            downloaded_file_path = os.path.join(temp_dir, basename)
            print("Downloading...", download_url)
            with (
                urllib.request.urlopen(download_url) as response,
                open(downloaded_file_path, "wb") as f,
            ):
                while chunk := response.read(4096):
                    f.write(chunk)

            print("Extracting...")
            with tarfile.open(downloaded_file_path) as tar:
                # tar.extractall(temp_dir, filter="data")
                tar.extractall(temp_dir)

            extracted_stem, *_ = os.path.splitext(basename)
            extracted_dir = os.path.join(temp_dir, extracted_stem)
            print("Configure...")
            ret = subprocess.run(
                [
                    os.path.join(extracted_dir, "configure"),
                    f"--prefix={site.USER_BASE}",
                    "--with-ensurepip=no",
                ],
                cwd=extracted_dir,
                capture_output=True,
                check=True,
                text=True,
            )

            if ret.stderr:
                print(ret.stderr)
                continue

            print("Make...")
            ret = subprocess.run(
                ["make", "-j", str(os.cpu_count())],
                cwd=extracted_dir,
                capture_output=True,
                check=True,
                text=True,
            )

            # if ret.stderr:
            #     print(ret.stderr)
            #     continue

            print("Make altinstall ...")
            ret = subprocess.run(
                ["make", "altinstall"],
                cwd=extracted_dir,
                capture_output=True,
                check=True,
                text=True,
            )

            if ret.stderr:
                print(ret.stderr)

    # subprocess.run(["tput", "bel"])


if __name__ == "__main__":
    main()
