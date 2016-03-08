#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% hive.image %>:<% hive.major %>.<% hive.minor %>"

docker push ${image}
docker push ${image}.${id}
