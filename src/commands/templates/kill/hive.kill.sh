#!/bin/bash
set -euo pipefail

container="<% __SERVICE_NAME__.name %>"

docker kill ${container}
docker rm   ${container}
