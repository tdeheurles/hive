#!/bin/bash
set -euo pipefail

id="<% cli.id %>"
image="<% hive.image %>:<% hive.major %>.<% hive.minor %>"

cp -r ../../../src .

docker build -t ${image} .
docker tag ${image} ${image}.${id}

rm -r src
