#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __main__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


# import datetime
import sys
import config
import logging
import commands
from provider.vbox import VBox
from provider.network import HostNetwork


vm_infos = {
    "ip": "172.16.16.100",
    "network": "172.16.16.1",
    "netmask": "255.255.255.0",
    "hostname": "fregate-001",
    "box_url": "boxes/fregate-base.ova",
}

def main():
    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)15s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logging.info("Fregate {}".format('1.0'))
    cfg = config.read()
    vm_infos["config"] = cfg
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
        commands.ssh(vm)
    elif args.action == "status":
        commands.status()
    elif args.action == "down":
        commands.down()
    elif args.action == "services":
        if args.add:
            commands.services('add', args.add, vm)
        if args.remove:
            commands.services('remove', args.remove, vm)
        if args.clean:
            commands.services('clean', args.clean, vm)
        if args.describe:
            commands.services('describe', args.describe, vm)
    return 0

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Cancel")
        commands.clean()
        sys.exit(1)
