#!/bin/bash

# fail fast
set -euo pipefail

./generate.sh 0

./hive $@
