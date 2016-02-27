#!/bin/bash

docker build -t <% image.__SERVICE_NAME__ %> .
docker tag <% image.__SERVICE_NAME__ %>.<% args.id %>
