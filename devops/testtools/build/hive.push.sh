#!/usr/bin/env bash

id="<% cli.id %>"
container="<% testtools.image %>:<% testtools.major %>.<% testtools.minor %>"

# fail fast
set -euo pipefail

docker id --no-cache -t ${container} .
docker tag -f ${container} ${container}.${id}
