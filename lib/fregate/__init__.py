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

network = {
    "ip": "172.16.16.1",
    "mask": "255.255.255.0"
}

vmlist = [
    {
        "ip": "172.16.16.100",
        "network": "172.16.16.1",
        "netmask": "255.255.255.0",
        "hostname": "fregate-001",
        "box_url": "http://repository.dotfile.eu/fregate-base-v1.ova",
    },
    {
        "ip": "172.16.16.101",
        "network": "172.16.16.1",
        "netmask": "255.255.255.0",
        "hostname": "fregate-002",
        "box_url": "http://repository.dotfile.eu/fregate-base-v1.ova",
    },
]


@atexit.register
def onexit():
    logger.info("Exiting ..")
    sys.exit(0)


def main():
    global logger
    global hostnetwork

    hostnetwork = None
    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)15s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('fregate')
    logger.debug("Fregate {}".format('1.0'))
    cfg = config.read()
    args = commands.parse_args()
    if args.action == "up":
        commands.up(cfg, vmlist, network)
    elif args.action == "clean":
        commands.clean(network=network)
    elif args.action == "ssh":
        commands.ssh(cfg, vmlist, args.vm_name)
        sys.exit(0)
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
