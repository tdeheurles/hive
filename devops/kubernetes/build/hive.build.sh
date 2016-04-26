#!/bin/bash
set -euo pipefail

image="<% kubernetes.image %>"
tag="<% cli.kubernetes_version %>"

docker build -t ${image} .
docker tag ${image} ${image}:${tag}
