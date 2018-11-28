#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : network.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import re
import logging
from commons.shell import execute
from commons.utils import fatal


class HostNetwork:
    def __init__(self, ip=None, mask=None):
        self.ip = ip
        self.mask = mask
        self.name = None

    def create(self):
        """ @params ip hostonly network ip
            @params netmask hostonly network mask
        """
        code, output = execute([
            "vboxmanage", "hostonlyif", "create"
        ], stdout=True)
        if code is not 0:
            fatal("Failed to create new host only network")
        for line in output:
            if line is not None:
                net_name = re.search("'.+'", line)
                if net_name is not None:
                    self.name = re.sub("'", '', net_name.group(0))
                    code = execute([
                        "vboxmanage", "hostonlyif",
                        "ipconfig", self.name, "--ip", self.ip
                    ])
                    if code is not 0:
                        fatal("Failed to update network config")
        logging.debug("Network {} is created".format(self.name))
        return self.name

    def delete(self):
        """ @params net_name Virtualbox HostOnlyNetwork name
        """
        code = execute([
            "vboxmanage", "hostonlyif", "remove", self.name
        ])
        if code is not 0:
            fatal("Failed to delete new host only network")
        logging.debug("Network {} is deleted".format(self.name))
        return 0

    def attach(self, vm):
        """ @params vm_name Machine name or uuid
            @params net_name Hostonly network name
        """
        code = execute([
            "vboxmanage", "modifyvm", vm.name, "--hostonlyadapter1", self.name
        ])
        if code is not 0:
            fatal("Failed to attach {} to {}".format(self.name, vm.name))
        code = execute([
            "vboxmanage", "modifyvm", vm.name, "--nic1", "hostonly"
        ])
        if code is not 0:
            fatal("Failed to attach {} to {}".format(self.name, vm.name))
        logging.debug("Sucessfully attached {} to {}"
                      .format(self.name, vm.name))
        vm.box_network = self
        return 0
