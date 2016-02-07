#!/bin/bash

if [[ $# == 0 ]];then
  echo "usage:"
  echo "  $0 BUILD_NUMBER"
  exit 1
fi
build=$1

echo "Our program will build with the number $build"
