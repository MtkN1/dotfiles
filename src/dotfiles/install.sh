#!/bin/bash -eux

mkdir --parents "${HOME}/.bashrc.d"
cp -rT $(dirname "${0}")/.bashrc.d "${HOME}/.bashrc.d"
