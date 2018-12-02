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
from fregate.commons.shell import logging
from fregate.commons.rke import rke


logger = logging.getLogger("kubernetes")


def up(cfg):
    logger.info("Kubernetes is deploying ...")
    rke('up', config=cfg)
    logger.info("Kubernetes .. OK")


def remove():
    logger.info("Kubernetes is undeploying ...")
    rke('remove --force')


def clean():
    remove()
    # try:
    #     with open(RKECFG, 'r') as f:
    #         cfg = yaml.load(f.read())
    # except Exception:
    #     fatal("Failed to open {}".format(RKECFG))
    # else:
    #     vms = cfg['nodes']
    #     for v in vms:
    #         config = {'ssh':
    #                   {'privkey': v['ssh_key_path'],
    #                    'user': v['user'],
    #                    'port': v['port']}}
    #         vm = VBox(ip=v['address'], config=config)
    #         ssh_cmd = vm.get_sshcmd()
    #         cmd = " 'bash -s' < 'scripts/clean_k8s.sh'"
    #         remove_cmd = ssh_cmd + cmd
    #         code = execute(remove_cmd, stdout=False, shell=True)
    #     kubecfg_cmd = 'rm {}'.format(kubeconfig)
    #     code, output = execute(kubecfg_cmd, stdout=True)
    #     if code != 0:
    #         logger.critical("Clean kubeconfing failed {}: {}".format(code, output))
    #     logger.info("Kubernetes cleaned")
    #     return True
