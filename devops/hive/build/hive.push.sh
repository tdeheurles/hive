#!/bin/bash
set -euo pipefail

image="<% hive.image %>:<% hive.major %>.<% hive.minor %>--docker<% hive.docker %>"
image_with_build_number="<% hive.image %>:<% hive.major %>.<% hive.minor %>.<% cli.id %>--docker<% hive.docker %>"

docker push ${image}
docker push ${image_with_build_number}
