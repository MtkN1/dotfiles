#!/bin/bash -eux

for script in $(dirname "${0}")/binary.d/*.sh; do
    "${script}"
done
