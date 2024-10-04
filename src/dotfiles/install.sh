#!/bin/bash -eux

mkdir --parents "${HOME}/.bashrc.d"
cp -rT $(dirname "${0}")/.bashrc.d "${HOME}/.bashrc.d"
cp -T $(dirname "${0}")/.bash_aliases "${HOME}/.bash_aliases"