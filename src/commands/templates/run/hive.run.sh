#!/bin/bash
set -euo pipefail

image="<% __SERVICE_NAME__.image %>"

docker kill ${image} 2&> /dev/null || true
docker run                \
  -t <% ${image} %> \
  -d <% ${image} %>.<% args.id %>
