#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __main__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import sys
import logging
import commands
from machine import VBox
from machine.network import HostNetwork


vm_infos = {
    "ip": "172.16.16.10",
    "network": "172.16.16.1",
    "netmask": "255.255.255.0",
    "hostname": "fregate",
    "box_url": "/home/tonychg/Documents/fregate-base.ova",
}


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Fregate {}".format('1.0'))
    args = commands.parse_args()
    vm = VBox(**vm_infos)
    if args.action == "up":
        hostnetwork = HostNetwork(ip=vm_infos["network"],
                                  mask=vm_infos["netmask"])
        hostnetwork.create()
        commands.up(vm, hostnetwork)
    elif args.action == "clean":
        commands.clean()
    elif args.action == "ssh":
        commands.ssh(vm, identity_file=".fregate.d/id_rsa", user="root")
    elif args.action == "status":
        commands.status()
    sys.exit(0)
