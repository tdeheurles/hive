#!/bin/bash

KUBERNETES_VERSION="<% cli.kubernetes_version %>"
KUBERNETES_IMAGE="<% kubernetes.base %>"
THIS_IMAGE="<% kubernetes.image %>"

sed -i \
  's|"--insecure-bind-address=127.0.0.1",|"--insecure-bind-address=0.0.0.0", "--insecure-port=8080", |g' \
  /etc/kubernetes/manifests/master.json

FILES="master.json kube-proxy.json"
for FILE in ${FILES}
do
    FILE_PATH=/etc/kubernetes/manifests/${FILE}

    sed -i \
        "s|${KUBERNETES_IMAGE}|${THIS_IMAGE}|g" \
        ${FILE_PATH}
done
