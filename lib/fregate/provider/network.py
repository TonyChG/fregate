# coding: utf-8
# =============================================================================
# Name     : network.py
# Function : VirtualBox CLI Wrapper
#            Basic network configuration
#            HostNetwork (Host only network)
#            Create a virtualbox host only network
#            Attach a virtualmachine to a network
#            Delete
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import re
import logging
from lib.fregate.commons.shell import execute
from lib.fregate.commons.utils import fatal


class HostNetwork:
    @staticmethod
    def list(network={}):
        """ List mapping host only network from config file
        """
        code, output = execute([
            "vboxmanage", "list", "hostonlyifs"
        ], stdout=True)
        if code is not 0:
            fatal("Failed to list host only network")
        networks = []
        ip_match = False
        name = ""
        for line in output:
            if line is not None:
                search_name = re.search("Name:[\t ]+vboxnet[0-9]+",
                                        line.strip())
                if search_name is not None:
                    name = re.sub("Name:[\t ]+", "", search_name.group(0))
                if re.search(network["ip"], line.strip()) is not None:
                    ip_match = True
                if re.search(network["mask"], line.strip()) is not None \
                        and ip_match:
                    ip_match = False
                    networks.append(HostNetwork(
                        ip=network["ip"],
                        name=name,
                        mask=network["mask"]
                    ))
        return networks

    def __init__(self, ip=None, mask=None, name=None):
        self.ip = ip
        self.mask = mask
        self.name = name
        self.logger = logging.getLogger("hostnetwork")

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
        self.logger.debug("Network {} is created".format(self.name))
        return self.name

    def delete(self):
        """ @params net_name Virtualbox HostOnlyNetwork name
        """
        code = execute([
            "vboxmanage", "hostonlyif", "remove", self.name
        ])
        if code is not 0:
            fatal("Failed to delete host only network {}".format(self.name))
        self.logger.debug("Network {} is deleted".format(self.name))
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
        self.logger.debug("Sucessfully attached {} to {}"
                          .format(self.name, vm.name))
        vm.box_network = self
        return 0
