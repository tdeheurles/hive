#!/bin/bash
set -euo pipefail

id="<% args.id %>"
image="<% image.hive %>:<% version.hive.major %>.<% version.hive.minor %>"

cp -r ../../../src .

docker build -t ${image} .
docker tag ${image} ${image}.${id}

rm -r src
