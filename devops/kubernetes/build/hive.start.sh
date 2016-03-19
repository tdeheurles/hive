#!/bin/bash

PORT="8080"
for i in "${@}"; do
  case ${i} in
    -p|--port)  PORT=${2};             shift 2;;
    -*) echo "unknown option: $1" >&2; usage; exit 1;;
    *) ARGS="$@"; shift 1;;
  esac
done

FILES="master.json kube-proxy.json"
for FILE in ${FILES}
do
    FILE_PATH=/etc/kubernetes/manifests/${FILE}
    sed -i \
        "s/8080/${PORT}/g" \
        ${FILE_PATH}
done

/hyperkube kubelet                         \
    --address="0.0.0.0"                    \
    --allow-privileged=true                \
    --enable-server                        \
    --api-servers=http://localhost:${PORT} \
    --config=/etc/kubernetes/manifests     \
    --cluster-dns=10.0.0.10                \
    --cluster-domain=cluster.local         \
    --v=2
