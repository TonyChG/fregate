#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : kubernetes.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from __future__ import absolute_import
from commons.shell import execute
from commons.shell import logging
from .service import Service

class Kubernetes(Service):
    def __init__(self, rke_path='.fregate.d/services/kubernetes/'):
        super().__init__()
        self.rke_path = rke_path

    def add(self):
        rke = self.rke_path + 'rke up'
        logging.info("Kubernetes is deploying ...")
        code, output = execute(rke, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Add kubernetes failed {}: {}".format(code, output))
            return False
        logging.info("Kubernetes is deployed")
        return True

    def remove(self):
        rke = self.rke_path + 'rke remove --force'
        logging.info("Kubernetes is undeploying ...")
        code, output = execute(rke, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Remove kubernetes failed {}: {}".format(code, output))
            return False
            return False
        logging.info("Kubernetes is undeployed")
        return True

    def purge(self):
        self.remove()
        cmd = "docker stop $(docker ps | egrep -h 'k8s|etcd' | awk '{print $1}')"
        code, output = execute(cmd, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Purge kubernetes failed {}: {}".format(code, output))
            return False
            return False
        logging.info("Kubernetes is purged")
        return True

    def describe(self):
        print('describe')
