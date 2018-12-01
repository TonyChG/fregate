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
    def __init__(self, vm):
        self.name = None
        self.vm = vm
        self.description = None
        self.alias = None
        self.dependencies = []
        self.state = False

