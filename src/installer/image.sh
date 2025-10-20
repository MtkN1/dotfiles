#!/bin/bash -eux

images=(
    # base images
    mcr.microsoft.com/devcontainers/base:alpine
    mcr.microsoft.com/devcontainers/base:trixie
    mcr.microsoft.com/devcontainers/base:noble
    mcr.microsoft.com/devcontainers/universal:2-linux

    # language images
    python:3.13-slim-trixie
    python:3.13-trixie
    mcr.microsoft.com/devcontainers/python:3.13-trixie
)

for image in "${images[@]}"; do
    docker pull "$image"
done
