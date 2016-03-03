#!/bin/bash
set -euo pipefail

image="<% __SERVICE_NAME__.name %>"

docker kill ${image}
