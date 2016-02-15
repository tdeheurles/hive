#! /bin/bash

if [[ $# != 1 ]];then
  echo "usage:"
  echo "  $0 BUILD_ID"
  exit 1
fi
build=$1

# fail fast
set -euo pipefail

./hive -v script hive_run --config build/config.yml //build/hive build.sh build ${build}
