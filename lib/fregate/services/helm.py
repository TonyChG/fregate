#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : helm.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from __future__ import absolute_import
from fregate.commons.shell import execute, logging
from fregate.commons.utils import fatal
from fregate.commons.kubectl import kubectl
from fregate.commons.rke import rke
from fregate.commons.helm import helm
from fregate.provider.vbox import VBox
import yaml

from .service import Service

def add():
    kubectl('-n kube-system create sa tiller')
    kubectl('create clusterrolebinding tiller \
            --clusterrole\
            cluster-admin\
            --serviceaccount=kube-system:tiller')
    # Init helm
    helm('init --skip-refresh --upgrade --service-account tiller')
    helm('repo update')
    logging.info("Helm .. OK")
    return True


def remove():
    helm('reset')


def clean():
    pass
