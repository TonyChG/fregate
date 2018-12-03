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
import fregate.config as config
import fregate.commands as commands
from fregate.commons.kubectl import kubectl
import yaml

__version__ = "0.0.2"


@atexit.register
def onexit():
    logging.info("Exiting ..")
    sys.exit(0)


def _setup_logging():
    global logger
    # Setup logging
    logformat = '[%(levelname)-8s%(relativeCreated)8d]'\
        ' [%(name)s] %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('fregate')
    logger.debug("-"*30)
    logger.debug("         Fregate {}".format(__version__))


def execute_binary(args):
    kubectl((" ".join(args[1:])))


def run(args, cfg, infra):
    """ Running correspondant command for action in command line
    """
    if args.action == "up":
        commands.up(cfg, infra, daemonize=args.daemonize,
                    cached=args.cached)
    elif args.action == "clean":
        commands.clean(network=infra["network"])
    elif args.action == "ssh":
        commands.ssh(cfg, infra["nodes"], args.vm_name)
        sys.exit(0)
    elif args.action == "status":
        commands.status(cfg, infra["nodes"])
    elif args.action == "down":
        commands.down(cfg, infra["nodes"])
    elif args.action == "service":
        service_name = args.name
        service_state = args.state
        commands.service_update(service_name,
                                service_state,
                                cfg=cfg, infra=infra)
    return 0


def main():
    _setup_logging()
    # Read config and command line
    cfg = config.read()
    args = commands.parse_args()
    if type(args) is list:
        return execute_binary(args)
    try:
        # Try to open default config file
        with open(args.configfile) as f:
            infra = yaml.load(f.read())
    except Exception:
        # Failed to read default config file
        logger.critical("Failed to open {}".format(args.configfile))
        sys.exit(-1)
    else:
        # Run command line
        return run(args, cfg, infra)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
