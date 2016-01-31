#!/bin/bash

if [[ $# != 1 ]];then
  echo "usage: require build id"
  echo "ie: $0 BUILD_ID"
  exit 1
fi
build=$1

container="container"

. ../config.sh

mkdir -p $container
cp Dockerfile        $container/Dockerfile
cp install.sh        $container/install.sh
cp ../../src/main.py $container/main.py

sed -i "s|__OS__|$os|g"                 $container/Dockerfile
sed -i "s|__MAINTAINER__|$maintainer|g" $container/Dockerfile

docker build -t $hiveContainer $container/.
docker tag -f $hiveContainer $hiveContainer.$build
