#!/bin/bash -eux

if ! command -v gcloud >/dev/null 2>&1; then
    sudo apt-get --no-install-recommends -y install apt-transport-https ca-certificates gnupg curl
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    sudo apt-get update
    sudo apt-get --no-install-recommends -y install google-cloud-cli
else
    sudo apt-get upgrade -y google-cloud-cli
fi
