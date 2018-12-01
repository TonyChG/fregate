#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : utils.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import sys
import logging


def fatal(message, exception=None, exit_code=1):
    logging.critical(message)
    if exception is not None:
        logging.debug(exception)
    sys.exit(exit_code)
