#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% local_cluster_proxy.image %>:<% local_cluster_proxy.major %>.<% local_cluster_proxy.minor %>"

docker push ${image}
docker push ${image}.${id}
