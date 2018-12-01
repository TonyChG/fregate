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


def _setup_logging():
    global logger
    # Setup logging
    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('fregate')
    logger.debug("-"*30)
    logger.debug("         Fregate {}".format('1.0'))


def run(args, cfg, vmlist, network):
    """ Running correspondant command for action in command line
    """
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


def main():
    _setup_logging()
    # Read config and command line
    cfg = config.read()
    args = commands.parse_args()
    try:
        # Try to open default config file
        with open(args.configfile) as f:
            infra = yaml.load(f.read())
            network = infra.get("network")
            vmlist = infra.get("nodes")
    except Exception:
        # Failed to read default config file
        logger.critical("Failed to open {}".format(args.configfile))
        sys.exit(-1)
    else:
        # Run command line
        return run(args, cfg, vmlist, network)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
