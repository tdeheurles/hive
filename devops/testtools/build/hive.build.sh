#!/usr/bin/env bash

id="<% cli.id %>"
container="<% testtools.image %>:<% testtools.major %>.<% testtools.minor %>"

# fail fast
set -euo pipefail

docker build --no-cache -t ${container} .
docker tag ${container} ${container}.${id}
