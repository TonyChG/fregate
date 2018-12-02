#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : base.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


class Service:
    def __init__(self, vmlist, dependencies=[]):
        self.name = None
        self.vmlist = vmlist
        self.description = None
        self.alias = None
        self.dependencies = dependencies
        self.state = False

