#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : kubectl.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from __future__ import absolute_import
from subprocess import call
from .common import kubeconfig
from .common import binary


def kubectl(command):

    base_cmd = '{}kubectl --kubeconfig={} '.format(binary, kubeconfig)
    command = ' '.join(command)
    print(command)
    final_cmd = base_cmd + command
    call(final_cmd, shell=True)
