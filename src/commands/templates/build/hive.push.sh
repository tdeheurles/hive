#!/bin/bash
set -euo pipefail

id="<% args.id %>"
image="<% __SERVICE_NAME__.image %>:<% __SERVICE_NAME__.major %>.<% __SERVICE_NAME__.minor %>"

docker push ${image}
docker push ${image}.${id}
