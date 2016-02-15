#!/bin/bash
set -euo pipefail

build="<% args.build %>"
image="<% image.hive %>:<% version.hive.major %>.<% version.hive.minor %>"

cp -r ../../src .

docker build -t ${image} .
docker tag ${image} ${image}.${build}

rm -r src
