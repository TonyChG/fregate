#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __init__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


from __future__ import absolute_import
from .kubernetes import Kubernetes
from .helm import Helm
from .dashboard import Dashboard
from .docker_registry import Registry

index = None

# Services singletons
def index(vmlist):
    index = {'kubernetes': Kubernetes(vmlist),
             'helm': Helm(vmlist),
             'dashboard': Dashboard(),
             'registry': Registry()}
    return index

