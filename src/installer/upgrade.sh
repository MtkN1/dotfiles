#!/bin/bash -eux

sudo apt-get update
sudo apt-get -y dist-upgrade

"$(dirname "${0}")/uv_tool.sh"
"$(dirname "${0}")/source.sh"
"$(dirname "${0}")/image.sh"