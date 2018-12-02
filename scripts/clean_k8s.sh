#!/bin/sh
# =============================================================================
# Name     : purge_k8s.sh
# Function :
# Usage    : ./k8s.sh
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

docker stop $(docker ps | egrep -h "(k8s|etcd|kube|rancher)" | awk '{print $1}')
docker rm $(docker ps -a | egrep -h "(k8s|etcd|kube|rancher)" | awk '{print $1}')
docker volume prune --force
