#!/bin/bash
set -euo pipefail

image="<% __SERVICE_NAME__.image %>"

docker kill ${image}
