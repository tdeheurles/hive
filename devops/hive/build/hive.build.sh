#!/bin/bash
set -euo pipefail

image="<% hive.image %>:<% hive.major %>.<% hive.minor %>--docker<% hive.docker %>"
image_with_build_number="<% hive.image %>:<% hive.major %>.<% hive.minor %>.<% cli.id %>--docker<% hive.docker %>"

cp -r ../../../src .

docker build -t ${image} .
docker tag ${image} ${image_with_build_number}

rm -r src
