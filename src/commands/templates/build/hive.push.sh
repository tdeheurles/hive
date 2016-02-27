#!/bin/bash

docker push <% image.__SERVICE_NAME__ %>
docker push <% image.__SERVICE_NAME__ %>.<% args.id %>
