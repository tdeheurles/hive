#! /bin/bash

id="<% cli.id %>"
container="<% gcloud.image %>:<% gcloud.major %>.<% gcloud.minor %>"

# fail fast
set -euo pipefail

docker build --no-cache -t ${container} .
docker tag ${container} ${container}.${id}
