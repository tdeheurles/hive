#!/bin/bash

if [[ $# != 1 ]];then
  echo "usage: require build id"
  echo "ie: $0 BUILD_ID"
  exit 1
fi
build=$1

. ../config.sh

docker push ${hiveContainer}
docker push ${hiveContainer}.${build}
