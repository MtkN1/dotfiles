from __future__ import annotations

import os.path
import platform
import shlex
import shutil
import subprocess
import tarfile
import tomllib
import urllib.parse
import urllib.request
from collections.abc import Sequence
from enum import Enum, auto
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

import attrs
import cattrs
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Mapping
    from http.client import HTTPResponse

    from _typeshed import StrOrBytesPath


class Hooks:
    def __init__(self) -> None:
        self._base_converter = cattrs.Converter()

    def argument_hook(self, value: Any, type: type[Argument], /) -> Argument:
        match value:
            case Argument():
                return value
            case str():
                return Argument(name=value, options=[])
            case _:
                return self._base_converter.structure(value, Argument)


def register_structure_hook(converter: cattrs.Converter, /) -> None:
    hooks = Hooks()
    converter.register_structure_hook(Argument, hooks.argument_hook)


@attrs.define(frozen=True, kw_only=True)
class Argument:
    name: str
    options: Sequence[str]


@attrs.define(frozen=True, kw_only=True)
class AptGetConfig:
    packages: Sequence[str]


@attrs.define(frozen=True, kw_only=True)
class SnapConfig:
    snaps: Sequence[Argument]


@attrs.define(frozen=True, kw_only=True)
class MiseConfig:
    core: Sequence[str]
    tools: Sequence[str]


@attrs.define(frozen=True, kw_only=True)
class UVPythonConfig:
    versions: Sequence[str]


@attrs.define(frozen=True, kw_only=True)
class UVToolConfig:
    packages: Sequence[Argument]


@attrs.define(frozen=True, kw_only=True)
class DockerConfig:
    images: Sequence[str]


@attrs.define(frozen=True, kw_only=True)
class ConfigRoot:
    apt_get: AptGetConfig
    snap: SnapConfig
    mise: MiseConfig
    uv_python: UVPythonConfig
    uv_tool: UVToolConfig
    docker: DockerConfig


def parse_config(data: object, converter: cattrs.Converter, /) -> ConfigRoot:
    return converter.structure(data, ConfigRoot)


def load_config(path: StrOrBytesPath, /) -> ConfigRoot:
    converter = cattrs.Converter()
    register_structure_hook(converter)
    with open(path, "rb") as stream:
        parsed = tomllib.load(stream)
    return parse_config(parsed, converter)


def sudo(arg: str, /, *args: str) -> list[str]:
    return [
        "sudo",
        "--",
        arg,
        *args,
    ]


class AptGet:
    @staticmethod
    def update() -> list[str]:
        return [
            "apt-get",
            "update",
        ]

    @staticmethod
    def install(package: str, /, *packages: str) -> list[str]:
        return [
            "apt-get",
            "--no-install-recommends",
            "-y",
            "install",
            "--",
            package,
            *packages,
        ]

    @staticmethod
    def dist_upgrade() -> list[str]:
        return [
            "apt-get",
            "-y",
            "dist-upgrade",
        ]

    @staticmethod
    def autopurge() -> list[str]:
        return [
            "apt-get",
            "-y",
            "autopurge",
        ]

    @staticmethod
    def autoclean() -> list[str]:
        return [
            "apt-get",
            "-y",
            "autoclean",
        ]


class Snap:
    @staticmethod
    def install(snap: str, /, *, options: Sequence[str]) -> list[str]:
        return [
            "snap",
            "install",
            *options,
            "--",
            snap,
        ]

    @staticmethod
    def refresh() -> list[str]:
        return [
            "snap",
            "refresh",
        ]


class Mise:
    @staticmethod
    def self_update() -> list[str]:
        return [
            "mise",
            "self-update",
            "-y",
        ]

    @staticmethod
    def use(tool: str, /, *tools: str) -> list[str]:
        return [
            "mise",
            "use",
            "-g",
            "--",
            tool,
            *tools,
        ]

    @staticmethod
    def upgrade() -> list[str]:
        return [
            "mise",
            "upgrade",
            "--bump",
        ]


class UV:
    @staticmethod
    def python_install(version: str, /, *versions: str) -> list[str]:
        return [
            "uv",
            "python",
            "install",
            "--",
            version,
            *versions,
        ]

    @staticmethod
    def python_upgrade() -> list[str]:
        return [
            "uv",
            "python",
            "upgrade",
        ]

    @staticmethod
    def tool_install(tool: str, /, *, options: Sequence[str]) -> list[str]:
        return [
            "uv",
            "tool",
            "install",
            *options,
            "--",
            tool,
        ]

    @staticmethod
    def tool_upgrade() -> list[str]:
        return [
            "uv",
            "tool",
            "upgrade",
            "--all",
        ]


class Docker:
    @staticmethod
    def pull(image: str, /) -> list[str]:
        return [
            "docker",
            "pull",
            "--",
            image,
        ]


class InstallResult(Enum):
    INSTALLED = auto()
    ALREADY_INSTALLED = auto()


def fetch_github_latest_tag(org: str, repo: str, /) -> str:
    path = PurePosixPath("/", org, repo, "releases", "latest")
    split_result = urllib.parse.SplitResult(
        "https",
        "github.com",
        path.as_posix(),
        "",
        "",
    )
    release_url = split_result.geturl()

    response: HTTPResponse = urllib.request.urlopen(release_url)
    response.close()

    split_result = urllib.parse.urlsplit(response.url)
    path = PurePosixPath(split_result.path)

    match path.parts:
        case [
            str() as _root,
            str() as _org,
            str() as _repo,
            "releases",
            "tag",
            str() as tag,
        ]:
            pass
        case _:
            raise ValueError(path)

    return tag


class SpecificInstaller:
    @staticmethod
    def mise() -> InstallResult:
        if shutil.which("mise") is not None:
            return InstallResult.ALREADY_INSTALLED

        org, repo = "jdx", "mise"
        tag = fetch_github_latest_tag(org, repo)

        uname = platform.uname()
        match uname.system:
            case "Linux":
                system = "linux"
            case _:
                raise ValueError(uname.system)
        match uname.machine:
            case "x86_64":
                machine = "x64"
            case _:
                raise ValueError(uname.machine)
        path = PurePosixPath(
            "/",
            org,
            repo,
            "releases",
            "download",
            tag,
            f"mise-{tag}-{system}-{machine}.tar.gz",
        )
        split_result = urllib.parse.SplitResult(
            "https",
            "github.com",
            path.as_posix(),
            "",
            "",
        )
        tarball_url = split_result.geturl()

        with TemporaryDirectory() as tmpdir:
            with (
                urllib.request.urlopen(tarball_url) as response,
                tarfile.open(fileobj=response, mode="r|gz") as tar,
            ):
                tar.extractall(tmpdir, filter="data")

            mise_bin = Path(tmpdir).joinpath("mise", "bin", "mise")

            home = Path.home()
            user_bin = home.joinpath(".local", "bin")
            user_bin.mkdir

            shutil.move(mise_bin, user_bin)

        return InstallResult.INSTALLED


def ensure_clean_path() -> str:
    home = Path.home()
    local_bin = home.joinpath(".local", "bin")
    local_bin.mkdir(parents=True, exist_ok=True)

    mise_shims = home.joinpath(".local", "share", "mise", "shims")

    path = os.path.pathsep.join(
        [
            str(mise_shims),
            str(local_bin),
            os.path.defpath,
        ]
    )
    return path


def check_call(
    console: Console,
    environ: Mapping[str, str],
    cmd: Sequence[StrOrBytesPath],
    /,
) -> int:
    console.rule(shlex.join(cmd))
    console.print()
    returncode = subprocess.run(cmd, env=environ, check=True).returncode
    console.print()
    return returncode


def execute_apt(
    console: Console,
    environ: Mapping[str, str],
    apt_get_config: AptGetConfig,
    /,
) -> None:
    check_call(
        console,
        environ,
        sudo(*AptGet.update()),
    )

    check_call(
        console,
        environ,
        sudo(*AptGet.install(*apt_get_config.packages)),
    )

    check_call(
        console,
        environ,
        sudo(*AptGet.dist_upgrade()),
    )
    check_call(
        console,
        environ,
        sudo(*AptGet.autopurge()),
    )
    check_call(
        console,
        environ,
        sudo(*AptGet.autoclean()),
    )


def execute_snap(
    console: Console,
    environ: Mapping[str, str],
    snap_config: SnapConfig,
    /,
) -> None:
    for snap in snap_config.snaps:
        check_call(
            console,
            environ,
            sudo(*Snap.install(snap.name, options=snap.options)),
        )

    check_call(
        console,
        environ,
        sudo(*Snap.refresh()),
    )


def execute_mise(
    console: Console,
    environ: Mapping[str, str],
    mise_config: MiseConfig,
    /,
) -> None:
    console.log("Ensuring Mise is installed...")
    result = SpecificInstaller.mise()

    if result == InstallResult.ALREADY_INSTALLED:
        check_call(
            console,
            environ,
            Mise.self_update(),
        )

    check_call(
        console,
        environ,
        Mise.use(*mise_config.core),
    )
    check_call(
        console,
        environ,
        Mise.use(*mise_config.tools),
    )

    check_call(
        console,
        environ,
        Mise.upgrade(),
    )


def execute_uv(
    console: Console,
    environ: Mapping[str, str],
    uv_python_config: UVPythonConfig,
    uv_tool_config: UVToolConfig,
    /,
) -> None:
    check_call(
        console,
        environ,
        UV.python_install(*uv_python_config.versions),
    )

    check_call(
        console,
        environ,
        UV.python_upgrade(),
    )

    for package in uv_tool_config.packages:
        check_call(
            console,
            environ,
            UV.tool_install(package.name, options=package.options),
        )

    check_call(
        console,
        environ,
        UV.tool_upgrade(),
    )


def execute_docker(
    console: Console,
    environ: Mapping[str, str],
    docker_config: DockerConfig,
    /,
) -> None:
    for image in docker_config.images:
        check_call(
            console,
            environ,
            Docker.pull(image),
        )


def main() -> None:
    console = Console()

    path = ensure_clean_path()
    environ = {"PATH": path, "HOME": str(Path.home())}

    config_path = Path(__file__).with_name("config.toml")
    config = load_config(config_path)

    execute_apt(console, environ, config.apt_get)
    # execute_snap(console, environ, config.snap)
    execute_mise(console, environ, config.mise)
    execute_uv(console, environ, config.uv_python, config.uv_tool)
    # execute_docker(console, environ, config.docker)


if __name__ == "__main__":
    main()
