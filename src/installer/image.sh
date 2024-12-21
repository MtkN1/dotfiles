#!/bin/bash -eux

images=(
    # base images
    mcr.microsoft.com/devcontainers/base:alpine
    mcr.microsoft.com/devcontainers/base:bookworm
    mcr.microsoft.com/devcontainers/base:noble
    mcr.microsoft.com/devcontainers/universal:2-linux

    # language images
    python:3.13-slim-bookworm
    python:3.13-bookworm
    mcr.microsoft.com/devcontainers/python:3.13-bookworm
)

for image in "${images[@]}"; do
    docker pull "$image"
done
