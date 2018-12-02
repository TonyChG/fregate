#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : kubectl.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from subprocess import call


def kubectl(command):
    kubeconfig = '.fregate.d/kube_config.yml'
    base_cmd = 'kubectl --kubeconfig={} '.format(kubeconfig)
    command = ' '.join(command)
    print(command)
    final_cmd = base_cmd + command
    call(final_cmd, shell=True)
