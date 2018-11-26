#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __main__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import re
import machine
import logging


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Fregate {}".format('1.0'))
    # Host only network
    net_name = machine.create_network("172.16.16.1", "255.255.255.0")
    # List vms
    vms = machine.list_vm()
    # Loop on vm if fregate is in name remove it
    for vm in vms:
        if re.search('fregate', vm["name"]) is not None:
            machine.delete(vm["uuid"])
    # Import base templates
    vm_name = machine.import_box("/home/tonychg/Documents/fregate-base.ova")
    # Update host only network
    machine.update_hostnetwork(vm_name, net_name)
    machine.start(vm_name)
    # machine.stop(vm_name)
