#!/bin/bash -eux

packages=(
    'python3'
    'python3-software-properties'
    'pkg-config'
)

source_packages=(
    'python3-defaults'
    'python3.12'
)

sudo apt-get update
sudo apt-get --no-install-recommends -y install "${packages[@]}"

sudo /usr/bin/python3 -c 'from softwareproperties.SoftwareProperties import SoftwareProperties; SoftwareProperties(deb822=True).enable_source_code_sources()'

sudo apt-get update
sudo apt-get --no-install-recommends -y build-dep "${source_packages[@]}"

sudo apt-get -y dist-upgrade
sudo apt-get -y autoremove

for script in $(dirname "${0}")/apt.d/*.sh; do
    "${script}"
done
