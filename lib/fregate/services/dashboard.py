#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : dashboard.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from fregate.commons.helm import helm

def up():
    cmd = 'helm install stable/kubernetes-dashboard --name kubernetes-dashboard --namespace kube-system'
    helm(cmd)

def down():
    cmd = 'helm delete kubernetes-dashboard'
    helm(cmd)

def clean():
    cmd = 'helm delete --purge kubernetes-dashboard'
    helm(cmd)


