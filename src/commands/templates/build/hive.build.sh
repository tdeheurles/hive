#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% __SERVICE_NAME__.image %>:<% __SERVICE_NAME__.major %>.<% __SERVICE_NAME__.minor %>"

docker build -t ${image} .
docker tag ${image} ${image}.${id}
