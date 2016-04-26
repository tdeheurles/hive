#!/bin/bash
set -euo pipefail

container="<% local_cluster_proxy.name %>"

docker kill ${container}
docker rm   ${container}
