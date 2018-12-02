#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : helm.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from subprocess import call
from .common import kubeconfig

def helm(commands):
    cmd = ""
    for command in commands:
        command = ' '.join(command)
        cmd += "bin/helm --kubeconfig='{}' {}; ".format(kubeconfig, command)
    print(cmd)
    call(cmd, shell=True)

