#!/bin/bash -eux

packages=(
    'hatch'
    'pdm'
    'poetry'
    'ruff'
)

_install_dir="${CARGO_HOME:-${HOME}/.cargo}/bin"
_user_local_bin="${HOME}/.local/bin"
_completions_dir="${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions"

# Check
if ! command -v "${_install_dir}/uv" >/dev/null 2>&1; then
    eixt 1
fi

# Install (package name == Command name)
for package in "${packages[@]}"; do
    if ! command -v "${_user_local_bin}/${package}" >/dev/null 2>&1; then
        "${_install_dir}/uv" tool install "${package}"
    fi
done
# Install (package name != Command name)
if ! command -v "${_user_local_bin}/aws" >/dev/null 2>&1; then
    "${_install_dir}/uv" tool install awscli
fi
# Install (self-hosted)
if ! command -v "${_user_local_bin}/gpkg" >/dev/null 2>&1; then
    "${_install_dir}/uv" tool install --from git+https://github.com/MtkN1/gpkg.git gpkg
fi

# Upgrade
"${_install_dir}/uv" tool upgrade --all
"${_install_dir}/gpkg" upgrade

# Completions
mkdir --parents "${_completions_dir}"

## awscli
echo 'complete -C aws_completer aws' > "${_completions_dir}/aws"
## hatch
_HATCH_COMPLETE=bash_source "${_user_local_bin}/hatch" > "${_completions_dir}/hatch"
## pdm
"${_user_local_bin}/pdm" completion bash > "${_completions_dir}/pdm"
## poetry
"${_user_local_bin}/poetry" completions bash > "${_completions_dir}/poetry"
## ruff
"${_user_local_bin}/ruff" generate-shell-completion bash > "${_completions_dir}/ruff"
