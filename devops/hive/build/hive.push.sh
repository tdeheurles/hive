#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% image.hive %>:<% version.hive.major %>.<% version.hive.minor %>"

docker push ${image}
docker push ${image}.${id}
