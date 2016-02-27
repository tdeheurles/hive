#!/bin/bash

docker kill <% image.__SERVICE_NAME__ %> 2&> /dev/null || true
docker run                \
  -t <% image.__SERVICE_NAME__ %> \
  -d <% image.__SERVICE_NAME__ %>.<% args.id %>
