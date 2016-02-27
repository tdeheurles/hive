#!/bin/bash
set -euo pipefail

docker kill <% __SERVICE_NAME__.image %>
