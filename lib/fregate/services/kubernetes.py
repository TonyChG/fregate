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
from subprocess import call
from time import sleep
import yaml

from .service import Service

CACHEFOLDER = '.fregate.d/'
RKEPATH = 'bin/'
KUBECONFIG = CACHEFOLDER + 'kube_config.yml'
RKECFG = CACHEFOLDER + 'services/kubernetes/cluster.yml'

class Kubernetes(Service):
    def __init__(self, vmlist=None, bin_path=RKEPATH, cfg=RKECFG):
        super().__init__(vmlist)
        self.bin_path = bin_path
        self.cfg = cfg
        self.description = '''
        Kubernetes service:
            this service will deploy a kubernetes cluster,
            using the `cluster.yaml` fil.
            '''

    def add(self):
        rke = '{}rke up --config={}'.format(self.bin_path, self.cfg)
        logging.info("Kubernetes is deploying ...")
        #  code, output = execute(rke, wait=Trdocker volume prune --forceue, stdout=True, shell=True)
        call(rke, shell=True)
        #  rke add file in . so move it into .fregate.d
        logging.info("Kubernetes .. OK")
        return True

    def remove(self):
        rke = '{}rke remove --force  --config={}'.format(self.bin_path, self.cfg)
        logging.info("Kubernetes is undeploying ...")
        call(rke, shell=True)
        logging.info("Kubernetes removed .. OK")

    def clean(self):
        self.remove()
        try:
            with open(RKECFG, 'r') as f:
                cfg = yaml.load(f.read())
        except Exception:
            fatal("Failed to open {}".format(RKECFG))
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
                code = execute(remove_cmd, stdout=False, shell=True)
            kubecfg_cmd = 'rm {}'.format(KUBECONFIG)
            code, output = execute(kubecfg_cmd, stdout=True)
            if code != 0:
                logging.critical("Clean kubeconfing failed {}: {}".format(code, output))
            logging.info("Kubernetes cleaned")
            return True

    def describe(self):
        print(self.description)
