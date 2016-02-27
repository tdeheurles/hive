#!/bin/bash
set -euo pipefail

# python
apt-get update
apt-get install python python-pip -y
pip install pyyaml
apt-get remove python-pip -y
apt-get autoremove -y

# docker
apt-get install wget -y
cd /usr/bin
wget -O /usr/bin/docker https://get.docker.com/builds/Linux/x86_64/docker-latest
chmod 755 /usr/bin/docker
