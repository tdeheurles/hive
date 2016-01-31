#! /bin/bash

if [[ $# != 1 ]];then
  echo "usage:"
  echo "  $0 BUILD_ID"
  exit 1
fi
build=$1

cd build
. ./config.sh

cd hive
./build.sh $build

cd ../..
