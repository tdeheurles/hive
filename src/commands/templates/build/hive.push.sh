#!/bin/bash
set -euo pipefail

image="<% __SERVICE_NAME__.image %>"

docker push ${image}
docker push ${image}.<% args.id %>
