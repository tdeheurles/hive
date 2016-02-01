#!/bin/bash

apt-get update
apt-get install python python-pip -y
apt-get install python -y
pip install pyyaml
apt-get remove python-pip -y
apt-get autoremove -y
