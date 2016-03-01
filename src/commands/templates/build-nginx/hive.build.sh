#!/bin/bash

build="<% cli.id %>"
major="<% __SERVICE_NAME__.major %>"
minor="<% __SERVICE_NAME__.minor %>"
container="<% __SERVICE_NAME__.image %>:${major}.${minor}"

# fail fast
set -euo pipefail

docker build --no-cache -t ${container} .
docker tag ${container} ${container}.${build}
