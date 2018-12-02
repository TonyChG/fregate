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
from fregate.commons.shell import execute, follow
from fregate.commons.shell import logging
from fregate.commons.utils import fatal
from fregate.provider.vbox import VBox
from time import sleep
import yaml

from .service import Service

CACHEFOLDER = '.fregate.d/'
RKEPATH = '.fregate.d/bin/'
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
        self.logger = logging.getLogger("kubernetes")

    def add(self):
        # rke = self.path + 'rke up'
        self.logger.info("Kubernetes is deploying ...")
        code = follow(self.path +  "rke up", stdout=True)
        if code is not 0:
            self.logger.warning("Kubernetes deployment failed")
        else:
            kubecfg_cmd = 'mv {} {}'.format('kube_config_cluster.yml', KUBECONFIG)
            code, output = execute(kubecfg_cmd, wait=True, stdout=True, shell=True)
            if code != 0:
                self.logger.critical("Add kubernetes conf failed {}: {}".format(code, output))
                return code
            self.logger.info("Kubernetes .. OK")
        return code

    def remove(self):
        self.logger.info("Kubernetes is undeploying ...")
        code = follow(self.path + 'rke remove --force', shell=True)
        if code is 0:
            self.logger.info("Kubernetes removed .. OK")
            return code
        else:
            self.logger.warning("Failed to remove kubernetes")

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
                self.logger.critical("Clean kubeconfing failed {}: {}".format(code, output))
            self.logger.info("Kubernetes cleaned")
            return True

    def describe(self):
        print(self.description)
