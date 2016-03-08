#!/bin/bash

PORT="8080"
for i in "${@}"; do
  case ${i} in
    -p|--port)  PORT=${2};             shift 2;;
    -*) echo "unknown option: $1" >&2; usage; exit 1;;
    *) ARGS="$@"; shift 1;;
  esac
done

# Change to this solution when 1.2 is released
#FILES="master.json etcd.json kube-proxy.json"
#for FILE in ${FILES}
#do
#    FILE_PATH=/etc/kubernetes/manifests/${FILE}
#    sed -i \
#        "s/8080/${PORT}/g" \
#        ${FILE_PATH}
#done

#/hyperkube kubelet                         \
#    --containerized                        \
#    --hostname-override="127.0.0.1"        \
#    --address="0.0.0.0"                    \
#    --api-servers=http://localhost:${PORT} \
#    --config=/etc/kubernetes/manifests     \
#    --cluster-dns=10.0.0.10                \
#    --cluster-domain=cluster.local         \
#    --allow-privileged=true                \
#    --v=2

FILES="master.json"
for FILE in ${FILES}
do
    FILE_PATH=/etc/kubernetes/manifests/${FILE}
    sed -i \
        "s/8080/${PORT}/g" \
        ${FILE_PATH}
done

/nsenter \
    --target=1 \
    --mount \
    --wd=. \
    -- \
    ./hyperkube \
        kubelet \
            --hostname-override=127.0.0.1 \
            --address=0.0.0.0 \
            --api-servers=http://localhost:${PORT} \
            --config=etc/kubernetes/manifests \
            --cluster-dns=10.0.0.10 \
            --cluster-domain=cluster.local \
            --allow-privileged=true \
            --v=2
