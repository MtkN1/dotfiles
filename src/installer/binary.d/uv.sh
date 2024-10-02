#!/bin/bash -eux

_install_dir="${CARGO_HOME:-${HOME}/.cargo}/bin"

if ! command -v "${_install_dir}/uv" >/dev/null 2>&1; then
    curl -fsSL https://astral.sh/uv/install.sh | INSTALLER_NO_MODIFY_PATH=1 sh
else
    INSTALLER_NO_MODIFY_PATH=1 "${_install_dir}/uv" self update
fi

_completions_dir="${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions"
mkdir --parent "${_completions_dir}"
"${_install_dir}/uv" generate-shell-completion bash > "${_completions_dir}/uv"
"${_install_dir}/uvx" --generate-shell-completion bash > "${_completions_dir}/uvx"
