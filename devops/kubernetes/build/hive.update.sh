#!/bin/bash

KUBERNETES_VERSION="<% cli.kubernetes_version %>"
KUBERNETES_IMAGE="<% kubernetes.base %>"
THIS_IMAGE="<% kubernetes.image %>"

##'s|"--portal-net=10.0.0.1/24",|"--portal-net=10.0.0.1/24", "--insecure-bind-address=0.0.0.0", "--insecure-port=8080", |g' \
#sed -i \
#  's|"--portal-net=10.0.0.1/24",|"--insecure-bind-address=0.0.0.0", "--insecure-port=8080", |g' \
#  /etc/kubernetes/manifests/master.json
#
#FILES="master.json"
##FILES="master.json etcd.json kube-proxy.json"
#for FILE in ${FILES}
#do
#    FILE_PATH=/etc/kubernetes/manifests/${FILE}
#
#    sed -i \
#        "s|${KUBERNETES_IMAGE}|${THIS_IMAGE}|g" \
#        ${FILE_PATH}
#done
#

cat <<EOF > /etc/kubernetes/manifests/master.json
{
"apiVersion": "v1",
"kind": "Pod",
"metadata": {"name":"k8s-master"},
"spec":{
  "hostNetwork": true,
  "containers":[
    {
      "name": "controller-manager",
      "image": "${THIS_IMAGE}",
      "command": [
              "/hyperkube",
              "controller-manager",
              "--master=127.0.0.1:8080",
              "--v=2"
        ]
    },
    {
      "name": "apiserver",
      "image": "${THIS_IMAGE}",
      "command": [
              "/hyperkube",
              "apiserver",
              "--service-cluster-ip-range=10.0.0.1/24",
              "--insecure-bind-address=0.0.0.0",
              "--insecure-port=8080",
              "--etcd-servers=http://127.0.0.1:4001",
              "--min-request-timeout=300",
              "--allow-privileged=true",
              "--v=4"
        ]
    },
    {
      "name": "scheduler",
      "image": "${THIS_IMAGE}",
      "command": [
              "/hyperkube",
              "scheduler",
              "--master=127.0.0.1:8080",
              "--v=2"
        ]
    }
  ]
 }
}
EOF
