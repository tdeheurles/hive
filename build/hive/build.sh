#!/bin/bash

if [[ $# != 1 ]];then
  echo "usage: require build id"
  echo "ie: $0 BUILD_ID"
  exit 1
fi
build=$1

# fail fast
set -euo pipefail

container="container"

. ../config.sh

mkdir -p ${container}
rm -rf ${container}/* || true

cp Dockerfile    ${container}/Dockerfile
cp -r ../../src  ${container}/app

sed -i "s|__OS__|$os|g"                 ${container}/Dockerfile
sed -i "s|__MAINTAINER__|$maintainer|g" ${container}/Dockerfile

docker build -t ${hiveContainer} ${container}/.
docker tag -f ${hiveContainer} ${hiveContainer}.${build}
