#!/bin/bash -eux

_version="4.0.0"

if ! pkg-config libmpdec; then
    _oldpwd="$(pwd)"
    _tempdir="$(mktemp -d)"
    cd "${_tempdir}"
    curl -fsSL https://www.bytereef.org/software/mpdecimal/releases/mpdecimal-${_version}.tar.gz | tar -xz --strip-components=1
    ./configure
    make
    sudo make install
    sudo ldconfig /usr/local/lib
    cd "${_oldpwd}"
    rm -rf "${_tempdir}"
fi
