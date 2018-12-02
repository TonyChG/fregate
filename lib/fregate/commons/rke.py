#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : helm.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from fregate.commons.shell import follow, logging
from .common import rke_cluster
from .common import binary


def rke(command, config=rke_cluster):
    logger = logging.getLogger("rke")
    cmd = "{}rke {} --config {}".format(binary, command, config)
    code = follow(cmd, stdout=True,
                  pattern='time=".+" ')
    if code is not 0:
        logger.warning("rke command failed")
    return code
