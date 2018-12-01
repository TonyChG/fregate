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
import yaml


@atexit.register
def onexit():
    logger.info("Exiting ..")
    sys.exit(0)


def main():
    global logger
    global hostnetwork

    hostnetwork = None
    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('fregate')
    logger.debug("-"*30)
    logger.debug("         Fregate {}".format('1.0'))

    cfg = config.read()
    args = commands.parse_args()

    try:
        with open(args.configfile) as f:
            configfile = yaml.load(f.read())
            network = configfile.get("network")
            vmlist = configfile.get("nodes")
    except Exception:
        logger.critical("Failed to open nodes.yml")
        sys.exit(-1)

    if args.action == "up":
        commands.up(cfg, vmlist, network, daemonize=args.daemonize)
    elif args.action == "clean":
        commands.clean(network=network)
    elif args.action == "ssh":
        commands.ssh(cfg, vmlist, args.vm_name)
        sys.exit(0)
    elif args.action == "status":
        commands.status(cfg, vmlist)
    elif args.action == "down":
        commands.down(cfg, vmlist)
    return 0


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Cancel")
        sys.exit(0)
