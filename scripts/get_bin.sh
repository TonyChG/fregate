#!/bin/bash
# Author: github.com/dauliac
# Date:   12/02/18
# Version: 0.0.1
# Description:

target="../.fregate.d/bin"
helm_url="https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz"
rke_url="https://github.com/rancher/rke/releases/download/v0.2.0-rc1/rke_linux-amd64"
kubectl_url="https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"

mkdir -p ${target}
if ! [[ -f ${target}/helm ]]; then
    curl -sL "${helm_url}" | tar -vzxf - "linux-amd64/helm" --strip 1 && mv helm ${target}/
    chmod +x ${target}/helm
fi
if ! [[ -f ${target}/rke ]]; then
    curl -L "${rke_url}" -o ${target}/rke
    chmod +x ${target}/rke
fi
if ! [[ -f ${target}/kubectl ]]; then
    curl -L "${kubectl_url}" -o ${target}/kubectl
    chmod +x ${target}/kubectl
fi

