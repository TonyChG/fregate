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
from fregate.commons.shell import execute
from fregate.commons.shell import logging
from fregate.commons.utils import fatal
from fregate.commons.kubectl import kubectl
from fregate.commons.helm import helm
from fregate.provider.vbox import VBox
import yaml

from .service import Service

CONFIGPATH = 'cluster.yml'
CACHEFOLDER = '.fregate.d/'
HELMPATH = CACHEFOLDER + 'services/helm/'
KUBECONFIG = CACHEFOLDER + 'kube_config.yml'


class Helm(Service):
    def __init__(self, vmlist, path=HELMPATH):
        super().__init__(vmlist)
        self.path = path
        self.cmd = ['']
        self.description = '''
        Helm service:
            this service will deploy a Helm and tiller in kubernetes cluster,
            using the `cluster.yaml` fil.
        '''

    def add(self):
        # Add helm binary
        config = {'ssh': {
            'privkey': CACHEFOLDER + 'id_rsa',
            'user': 'root',
            'port': 22
        }}

        vm = VBox(hostname=self.vmlist[0]['hostname'], ip=self.vmlist[0]['ip'], config=config)
        scp_cmd = vm.get_sshcmd(
            scp=True,
            target='./bin/helm',
            dest='{}@{}:/usr/bin/helm'.format(vm.ssh_user, vm.ip))
        print(scp_cmd)
        code = execute(scp_cmd, wait=True, shell=True)

        code, output = execute(scp_cmd, wait=True, stdout=True)
        if code != 0:
            logging.critical("Add helm binary failed {}: {}".format(code, output))
            return False
        # Create helm kubernetes confs
        kubectl_helm_cmds = [['-n', 'kube-system', 'create', 'sa', 'tiller'],
                        ['--kubeconfig={}'.format(KUBECONFIG), 'create', 'clusterrolebinding', 'tiller', '--clusterrole', 'cluster-admin', '--serviceaccount=kube-system:tiller']]
        for cmd in kubectl_helm_cmds:
            kubectl(cmd)
        # Init helm
        helm_cmds = [['init', '--skip-refresh', '--upgrade', '--service-account', 'tiller'],
                    ['repo', 'update']]
        helm(helm_cmds, vm)
        #  for cmd in helm_cmds:
        #      code, output = execute(cmd, wait=True, stdout=True, shell=True)
        #      if code != 0:
        #          logging.critical("Init helm failed {}: {}".format(code, output))
        #          return False
        logging.info("Helm .. OK")
        return True


    def remove(self):
        rke = [self.rke_path + 'rke', 'remove', '--force']
        logging.info("Kubernetes is undeploying ...")
        code, output = execute(rke, wait=True, stdout=True, shell=True)
        if code != 0:
            logging.critical("Remove kubernetes .. FAILED {}: {}".format(code, output))
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
        print(self.description)
