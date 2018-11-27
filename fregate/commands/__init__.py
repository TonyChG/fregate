#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __init__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


from machine import VBox
from argparse import ArgumentParser
import logging
import socket
import time
import signal
import sys
import re

vms = []


def parse_args():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='Action to execute')
    subparsers.dest = 'action'
    subparsers.required = True
    up_parser = subparsers.add_parser('up')
    up_parser.add_argument("-d, --daemon", action="store_true",
                           default=False)
    subparsers.add_parser('clean')
    subparsers.add_parser('ssh')
    subparsers.add_parser('status')
    return parser.parse_args()


def sigint_handler(signum, frame):
    network = None
    for vm in vms:
        logging.info("Stop {}".format(vm.name))
        vm.stop()
        while vm.infos["VMState"] == "running":
            time.sleep(1)
            vm.getinfo()
        network = vm.box_network
    logging.info("Delete {}".format(vm.box_network.name))
    network.delete()
    sys.exit(0)


def ssh(vm, identity_file=None, user=None):
    vm.ssh(identity_file=identity_file, user=user)


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


def up(vm, network, wait_port=22):
    """ Start default test infra
    """
    signal.signal(signal.SIGINT, sigint_handler)
    # - Import base templates
    # - Create Host only network
    vm.import_box()
    # Update host only network
    network.attach(vm)
    vm.start(env={
        "VM_IP": vm.ip,
        "VM_HOSTNAME": vm.hostname,
        "VM_NETMASK": vm.netmask
    })
    while ssh_is_responding(vm.ip, wait_port) is False:
        time.sleep(1)
    while True:
        vm.getinfo()
        logging.info("{} is running with address {}".format(vm.name, vm.ip))
        vms.append(vm)
        input("Ctrl+c to quit\n")
    print()


def clean():
    """ Remove all box with name fregate
    """
    vms = VBox.list()
    for vm in vms:
        if re.search('^fregate', vm['name']):
            VBox.destroy(vm['uuid'])


def status():
    vms = VBox.list()
    for vm in vms:
        if re.search('^fregate', vm['name']):
            logging.info("Founded {}".format(vm['name']))
