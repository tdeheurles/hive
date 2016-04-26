#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% __SERVICE_NAME__.image %>:<% __SERVICE_NAME__.major %>.<% __SERVICE_NAME__.minor %>"
container="<% __SERVICE_NAME__.name %>"

docker kill ${container} 2&> /dev/null || true
docker rm   ${container} 2&> /dev/null || true
docker run -d         \
  --name ${container} \
  ${image}.${id}
