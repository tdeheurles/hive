#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% local_cluster_proxy.image %>:<% local_cluster_proxy.major %>.<% local_cluster_proxy.minor %>"
container="<% local_cluster_proxy.name %>"

docker kill ${container} 2&> /dev/null || true
docker rm   ${container} 2&> /dev/null || true
docker run -d         \
  --name ${container} \
  -p 80:80 \
  ${image}.${id}
