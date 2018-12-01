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
from lib.fregate.commons.shell import execute
from lib.fregate.commons.shell import logging
from lib.fregate.commons.utils import fatal
from lib.fregate.provider.vbox import VBox
import yaml

from .service import Service

CONFIGPATH = 'cluster.yml'

class Kubernetes(Service):
    def __init__(self, rke_path='.fregate.d/services/kubernetes/'):
        super().__init__()
        self.rke_path = rke_path

    def add(self):
        rke = [self.rke_path + 'rke', 'up']
        logging.info("Kubernetes is deploying ...")
        code, output = execute(rke, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Add kubernetes failed {}: {}".format(code, output))
            return False
        logging.info("Kubernetes .. OK")
        return True

    def remove(self):
        rke = [self.rke_path + 'rke', 'remove', '--force']
        logging.info("Kubernetes is undeploying ...")
        code, output = execute(rke, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Remove kubernetes .. FAILED {}: {}".format(code, output))
            return False
            return False
        logging.info("Kubernetes removed .. OK")
        return True

    def clean(self):
        self.remove()
        try:
            with open(CONFIGPATH, 'r') as f:
                cfg = yaml.load(f.read())
        except Exception:
            fatal("Failed to open {}".format(CONFIGPATH))
        else:
            vms = cfg['nodes']
            for v in vms:
                config = {'ssh':
                          {'privkey': v['ssh_key_path'],
                           'user': v['user'],
                           'port': v['port']}}
                vm = VBox(ip=v['address'], config=config)
                ssh_cmd = vm.get_sshcmd()
                cmd = " 'bash -s' < 'scripts/clean_k8s.sh'"
                remove_cmd = ssh_cmd + cmd
                code, output = execute(remove_cmd, wait=True, stdout=True, shell=True)
                if code != 0:
                    logging.critical("Clean kubernetes failed {}: {}".format(code, output))
                logging.info("Kubernetes cleaned")
            return True

    def describe(self):
        print('''
        Kubernetes service:
            this service will deploy a kubernetes cluster,
            using the `cluster.yaml` fil.
            ''')
