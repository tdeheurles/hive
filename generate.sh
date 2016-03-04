#! /bin/bash

if [[ $# != 1 ]];then
  echo "usage:"
  echo "  $0 ID"
  exit 1
fi
id=$1

# fail fast
set -euo pipefail

./hive -v do build devops hive id ${id}
