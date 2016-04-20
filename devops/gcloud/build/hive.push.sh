#! /bin/bash

id="<% cli.id %>"
container="<% gcloud.image %>:<% gcloud.major %>.<% gcloud.minor %>"

# fail fast
set -euo pipefail

docker push ${container}
docker push ${container}.${id}
