#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __main__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import socket
import time
import signal
import sys
import re
import machine
import logging
from argparse import ArgumentParser


vm = {
    "ip": "172.16.16.10",
    "network": "172.16.16.1",
    "netmask": "255.255.255.0",
    "hostname": "fregate",
    "box_name": "",
    "box_uuid": "",
    "box_url": "/home/tonychg/Documents/fregate-base.ova",
    "network_name": ""
}


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='Action to execute')
    subparsers.dest = 'action'
    subparsers.required = True
    start_parser = subparsers.add_parser('start')
    start_parser.add_argument("-d, --daemon", action="store_true",
                              default=False)
    subparsers.add_parser('clean')
    subparsers.add_parser('ssh')
    return parser.parse_args()


def sigint_handler(signum, frame):
    logging.info("Stop {}".format(vm["box_name"]))
    machine.stop(vm["box_name"])
    vm["box_infos"] = machine.get_vmstate(vm["box_name"])
    while vm["box_infos"]["VMState"] == "running":
        time.sleep(1)
        vm["box_infos"] = machine.get_vmstate(vm["box_name"])
    logging.info("Delete {}".format(vm["network_name"]))
    machine.delete_hostnetwork(vm["network_name"])
    sys.exit(0)


def ssh_connect(vm):
    machine.ssh(vm)


def ssh_is_responding(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.close()
    except (socket.timeout, socket.error):
        logging.warning("Failed to connect to {}".format(ip))
        return False
    else:
        return True


def start():
    """ Start default test infra
    """
    # Host only network
    vm["network_name"] = machine.create_network(vm["network"], vm["netmask"])
    # List vms
    # Import base templates
    vm["box_name"] = machine.import_box(vm["box_url"])
    # Update host only network
    machine.update_hostnetwork(vm["box_name"], vm["network_name"])
    machine.start(vm["box_name"], env={
        "VM_IP": vm["ip"],
        "VM_HOSTNAME": vm["hostname"],
        "VM_NETMASK": vm["netmask"]
    })

    ssh_port = 22
    while ssh_is_responding(vm["ip"], ssh_port) is False:
        time.sleep(1)
    while True:
        machine.get_vmstate(vm["box_name"])
        logging.info("{} is running with address {}"
                     .format(vm["box_name"], vm["ip"]))
        input("Ctrl+c to quit\n")


def clean():
    """ Remove all box with name fregate
    """
    vms = machine.list_vm()
    # Loop on vm if fregate is in name remove it
    for actual_vm in vms:
        if re.search('fregate', actual_vm["name"]) is not None:
            machine.stop(actual_vm["uuid"])
            machine.delete(actual_vm["uuid"])


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Fregate {}".format('1.0'))
    args = parse_args()
    if args.action == "start":
        start()
    elif args.action == "clean":
        clean()
    elif args.action == "ssh":
        ssh_connect(vm)
    sys.exit(0)
