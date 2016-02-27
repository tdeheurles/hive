#! /bin/bash

if [[ $# != 1 ]];then
  echo "usage:"
  echo "  $0 ID"
  exit 1
fi
id=$1

# fail fast
set -euo pipefail

./hive do build devops hive id ${id}
