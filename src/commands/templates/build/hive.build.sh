#!/bin/bash
set -euo pipefail

image="<% __SERVICE_NAME__.image %>"

docker build -t ${image} .
docker tag ${image} ${image}.<% args.id %>
