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
from .common import binary

def helm(commands):
    cmd = ""
    for command in commands:
        command = ' '.join(command)
        cmd += "{}helm --kubeconfig='{}' {}; ".format(binary, kubeconfig, command)
    print(cmd)
    call(cmd, shell=True)

