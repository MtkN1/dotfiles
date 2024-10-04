#!/bin/bash -eux

_install_dir="${CARGO_HOME:-${HOME}/.cargo}/bin"

if ! command -v "${_install_dir}/rustup" >/dev/null 2>&1; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path
fi
