#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __init__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


from provider.vbox import VBox
from commons.shell import execute
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
    subparsers.add_parser('down')
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
    for vm in vms:
        vm.delete()
    sys.exit(0)


def ssh(vm, identity_file=None, user=None):
    vm.ssh(identity_file=identity_file, user=user)


def ssh_attempt(ip, port=22, privkey=".fregate.d/id_rsa", user="root"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.close()
    except (socket.timeout, socket.error):
        logging.warning("Failed to connect to {}".format(ip))
        return False
    else:
        ssh_command = "ssh -q -i '{}' -o 'StrictHostKeyChecking=no'"\
            " -p {} {}@{} id -u".format(privkey, port, user, ip)
        code, output = execute(ssh_command, wait=True, stdout=True, shell=True)
        if code is 0 and int(output[0]) is 0:
            return True
        return False


def waiting_ssh(ip, port=22, user="root", privkey=".fregate.d/id_rsa"):
    trials = 0
    ssh_available = False
    while not ssh_available:
        if trials % 2 is 0:
            logging.info("Waiting up of SSH")
            ssh_available = ssh_attempt(ip, port=port,
                                        user=user, privkey=privkey)
        trials += 1
        if ssh_available is False:
            time.sleep(1)


def up(vm, network, wait_port=22):
    """ Start default test infra
    """
    signal.signal(signal.SIGINT, sigint_handler)
    # - Import base templates
    # - Create Host only network
    vm.import_box()
    # Update host only network
    network.attach(vm)
    # Start the vm
    vm.start()
    # Host ssh config
    host_ip = "127.0.0.1"
    host_port = 2222
    # Enable forwarding
    vm.forward_ssh(host_ip=host_ip, host_port=2222)
    # Wait for ssh to respond
    waiting_ssh(host_ip, port=host_port, privkey=".fregate.d/id_rsa")
    vm.launch_firstboot()
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


def down():
    """ Stop all box
    """
    vms = VBox.list()
    for vm in vms:
        if re.search('^fregate', vm['name']):
            VBox.force_stop(vm['uuid'])


def status():
    vms = VBox.list()
    for vm in vms:
        if re.search('^fregate', vm['name']):
            logging.info("Founded {}".format(vm['name']))
