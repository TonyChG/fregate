#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : config.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import yaml
from fregate.commons.utils import fatal


def read(configpath='fregate.yml'):
    try:
        with open(configpath, 'r') as f:
            cfg = yaml.load(f.read())
    except Exception:
        fatal("Failed to open {}".format(configpath))
    else:
        return cfg
