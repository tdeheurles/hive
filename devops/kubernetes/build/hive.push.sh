#!/bin/bash
set -euo pipefail

image="<% kubernetes.image %>"
tag="<% cli.kubernetes_version %>"

docker push ${image}
docker push ${image}:${tag}
