#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __init__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


# import datetime
import sys
import logging
import atexit
import lib.fregate.config as config
import lib.fregate.commands as commands
from lib.fregate.provider.vbox import VBox
from lib.fregate.provider.network import HostNetwork


vm_infos = {
    "ip": "172.16.16.100",
    "network": "172.16.16.1",
    "netmask": "255.255.255.0",
    "hostname": "fregate-001",
    "box_url": "http://repository.dotfile.eu/fregate-base-v1.ova",
}


@atexit.register
def onexit():
    logger.info("Exiting ..")
    sys.exit(0)


def main():
    global logger
    global hostnetwork

    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)15s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('fregate')
    logger.info("Fregate {}".format('1.0'))
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
    return 0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Cancel")
        sys.exit(0)
