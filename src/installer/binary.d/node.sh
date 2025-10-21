#!/bin/bash -eux

_install_dir="${HOME}/.local/bin"
_version='v22.14.0'
_stem="node-${_version}-linux-x64"
_url="https://nodejs.org/dist/${_version}/${_stem}.tar.xz"

if ! command -v "${_install_dir}/node" >/dev/null 2>&1 || [ "$(${_install_dir}/node -v)" != "$_version" ]; then
    _tempdir=$(mktemp -d)

    curl -fL "${_url}" | tar -C "${_tempdir}" -xJ

    mkdir --parent "${HOME}/.local"
    cp -rT "${_tempdir}/${_stem}/bin" "${HOME}/.local/bin"
    cp -rT "${_tempdir}/${_stem}/include" "${HOME}/.local/include"
    cp -rT "${_tempdir}/${_stem}/lib" "${HOME}/.local/lib"
    cp -rT "${_tempdir}/${_stem}/share" "${HOME}/.local/share"

    rm -rf "${_tempdir}"
fi

_completions_dir="${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions"
mkdir --parent "${_completions_dir}"
"${_install_dir}/npm" completion bash > "${_completions_dir}/npm"
