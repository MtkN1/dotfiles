#!/bin/bash -eux

packages=(
    'hatch'
    'pdm'
    'poetry'
    'ruff'
)

_completions_dir="${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions"

# Check
if ! command -v uv >/dev/null 2>&1; then
    exit 1
fi

# Install (package name == command name)
for package in "${packages[@]}"; do
    if ! command -v "${package}" >/dev/null 2>&1; then
        uv tool install "${package}"
    fi
done
# Install (package name != command name)
if ! command -v aws >/dev/null 2>&1; then
    uv tool install awscli
fi
# Install (self-hosted)
if ! command -v gpkg >/dev/null 2>&1; then
    uv tool install --from git+https://github.com/MtkN1/gpkg.git gpkg
fi

# Upgrade
uv tool upgrade --all
gpkg upgrade

# Completions
mkdir --parents "${_completions_dir}"

## awscli
echo 'complete -C aws_completer aws' > "${_completions_dir}/aws"
## hatch
_HATCH_COMPLETE=bash_source hatch > "${_completions_dir}/hatch"
## pdm
pdm completion bash > "${_completions_dir}/pdm"
## poetry
poetry completions bash > "${_completions_dir}/poetry"
## ruff
ruff generate-shell-completion bash > "${_completions_dir}/ruff"
