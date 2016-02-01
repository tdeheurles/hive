#! /bin/bash

if [[ $# != 1 ]];then
  echo "usage:"
  echo "  $0 BUILD_ID"
  exit 1
fi
build=$1

# fail fats
set -euo pipefail

. build/config.sh

cd build/hive
./build.sh $build

cd ../..
