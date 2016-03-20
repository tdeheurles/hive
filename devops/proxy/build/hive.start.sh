#!/bin/bash

set -euo pipefail

#       USAGE
# ================
HOST_PORT=""
CONTAINER_PORT=""
SERVICE=""
NAMESPACE=""
METHOD=""

for i in "${@}"; do
    case ${i} in
        -hp=*|--host-port=*)      HOST_PORT="${i#*=}";      shift 1;;
        -cp=*|--container-port=*) CONTAINER_PORT="${i#*=}"; shift 1;;
        -s=*|--service=*)         SERVICE="${i#*=}";        shift 1;;
        -n=*|--namespace=*)       NAMESPACE="${i#*=}";      shift 1;;
        -m=*|--method=*)          METHOD="${i#*=}";         shift 1;;
        -*) echo "unknown option: $1" >&2; usage; exit 1;;
        *) ARGS="$@"; break;;
    esac
done

if [[ ${HOST_PORT} == "" || ${CONTAINER_PORT} == "" || ${SERVICE} == "" || ${NAMESPACE} == "" || ${METHOD} == "" ]];then
    echo " "
    echo "Error, usage:"
    echo " "
    echo "  $0 --host-port=xxx --container-port=xxx --service==xxx --namespace=xxx --method=http"
    echo "  $0 --host-port=xxx --container-port=xxx --service==xxx --namespace=xxx --method=ws"
    echo "  $0 -hp=xxx -cp=xxx -s==xxx -n=xxx -m=http"
    echo "  $0 -hp=xxx -cp=xxx -s==xxx -n=xxx -m=ws"
    echo " "
    exit 1
fi


#  GET SERVICE IP
# ================
IP=${SERVICE}

#  COPY AND UPDATE METHOD FILE
# =============================
if [[ ${METHOD} == "HTTP" || ${METHOD} == "http" ]];then
    cp /tmp/http.nginx.conf /etc/nginx/nginx.conf
elif [[ ${METHOD} == "WS" || ${METHOD} == "ws" ]];then
    cp /tmp/ws.nginx.conf /etc/nginx/nginx.conf
fi

sed -i "s/__HOST_PORT__/${HOST_PORT}/g"           /etc/nginx/nginx.conf
sed -i "s/__CONTAINER_PORT__/${CONTAINER_PORT}/g" /etc/nginx/nginx.conf
sed -i "s/__SERVICE_IP__/${IP}/g"                 /etc/nginx/nginx.conf

#  START NGINX
# =============
nginx &

while true; do sleep 3600; done
