#!/bin/bash
# Author: github.com/dauliac
# Date:   12/02/18
# Version: 0.0.1
# Description:


# curl -LO https://storage.googleapis.com/kubernetes-helm/helm-v2.11.0-linux-amd64.tar.gz
tar xf helm-v2.11.0-linux-amd64.tar.gz
mv linux-amd64//helm helm
rm -Rvf linux-amd64

curl -lO https://github.com/rancher/rke/releases/download/v0.2.0-rc1/rke_linux-amd64
mv rke_linux-amd64 rke
# curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
chmod +x helm
chmod +x kubectl
chmod +x rke
