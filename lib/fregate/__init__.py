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
import yaml

__version__ = "0.0.1"


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
    logger.debug("         Fregate {}".format(__version__))


def run(args, cfg, infra):
    """ Running correspondant command for action in command line
    """
    if args.action == "up":
        commands.up(cfg, infra["nodes"], infra["network"],
                    daemonize=args.daemonize)
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
        # if args.add:
        #     commands.services('add', vmlist, args.add)
        # elif args.remove:
        #     commands.services('remove', vmlist, args.remove)
        # elif args.clean:
        #     commands.services('clean', vmlist, args.clean)
        # else:
        #     commands.services('describe', vmlist, args.describe)
    #  elif args.action == "kubectl":
    #      commands.kubectl(args.command)
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
