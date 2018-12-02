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
import yaml
import logging
from . import kubernetes

logger = logging.getLogger("service")


def gen_rke_template(dest, vms, rke={}):
    try:
        with open(dest, "w") as f:
            nodes = []
            for vm in vms:
                nodes.append({
                    "address": vm.ip,
                    "user": vm.ssh_user,
                    "role": vm.role,
                    "ssh_key_path": vm.ssh_privkey,
                    "port": vm.ssh_port
                })
            yaml.dump(dict({
                "nodes": nodes,
            }, **rke), f, default_flow_style=False)
            f.close()
    except Exception:
        logger.warning("Failed to create {}".format(dest))
        return -1
    else:
        return dest


def run(name, state, vms, infra={}):
    if name == 'kubernetes':
        cfg = gen_rke_template("/tmp/cluster.yml", vms,
                               rke=infra["rke"])
        kubernetes.up(cfg)
    # index = {'kubernetes': Kubernetes(vmlist),
    #          'helm': Helm(vmlist),
    #          'dashboard': Dashboard(),
    #          'registry': Registry()}
    # return index
    pass
