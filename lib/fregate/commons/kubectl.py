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
from fregate.commons.shell import execute, follow, logging
from .common import kubeconfig
from .common import binary


def kubectl(command):
    logger = logging.getLogger("kubectl")
    cmd = "{}kubectl --kubeconfig='{}' {}; ".format(binary, kubeconfig, command)
    code = follow(cmd, stdout=True,
                      pattern='time=".+" ')
    if code is not 0:
        logger.warning("rke command failed")
    return code
