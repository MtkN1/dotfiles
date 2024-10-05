#!/bin/bash -eux

for script in $(dirname "${0}")/source.d/*.sh; do
    "${script}"
done

for script in $(dirname "${0}")/source.d/*.py; do
    "${script}"
done
