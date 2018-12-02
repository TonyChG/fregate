#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : __init__.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from __future__ import absolute_import
from lib.fregate.provider.network import HostNetwork
from lib.fregate.provider.vbox import VBox
from lib.fregate.commons.shell import execute
from lib.fregate import services as svc
from subprocess import call
from argparse import ArgumentParser
import logging
import socket
import time
# import signal
# import sys
import os
import re

_vms = []
_firstforward_port = 2222
logger = logging.getLogger('fregate')


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-c, --config", dest="configfile",
                        default=os.getcwd()+"/nodes.yml",
                        help="Config path where vm specifications are store")
    subparsers = parser.add_subparsers(help='Action to execute')
    subparsers.dest = 'action'
    subparsers.required = True
    up_parser = subparsers.add_parser('up')
    up_parser.add_argument("-d, --daemon", action="store_true",
                           default=False, dest="daemonize")
    subparsers.add_parser('clean')
    ssh_parser = subparsers.add_parser('ssh')
    ssh_parser.add_argument("vm_name")
    subparsers.add_parser('status')
    subparsers.add_parser('down')
    parser_srv = subparsers.add_parser('services')
    parser_srv.add_argument("--add")
    parser_srv.add_argument("--remove")
    parser_srv.add_argument("--clean")
    parser_srv.add_argument("--describe")
    #  parser_srv = subparsers.add_parser('kubectl')
    #  parser_srv.add_argument('command', metavar='N', type=str, nargs='*',
                            #  help='kubectl <command>')
    return parser.parse_args()


def _get_vmlist(cfg, vmlist):
    for vm_info in vmlist:
        vm_info["config"] = cfg
        _vms.append(VBox(**vm_info))
        # _vms[-1].getinfo()


def ssh(cfg, vmlist, vm_name):
    _get_vmlist(cfg, vmlist)
    for vm in _vms:
        if vm.hostname == vm_name:
            vm.ssh()


def ssh_attempt(ip, port=22, privkey=".fregate.d/id_rsa", user="root"):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    try:
        s.connect((ip, port))
        s.close()
    except (socket.timeout, socket.error):
        return False
    else:
        ssh_command = "ssh -q -i '{}' -o 'StrictHostKeyChecking=no'"\
            " -p {} {}@{} id -u".format(privkey, port, user, ip)
        code, output = execute(ssh_command, wait=True, stdout=True, shell=True)
        if code is 0 and int(output[0]) is 0:
            return True
        return False


def waiting_ssh(vm):
    trials = 0
    ssh_available = False
    while not ssh_available:
        if trials % 2 is 0:
            vm.logger.info("Waiting SSH connection ...")
            ssh_available = ssh_attempt('127.0.0.1', port=vm.forwared_port,
                                        user=vm.ssh_user,
                                        privkey=vm.ssh_privkey)
        trials += 1
        if ssh_available is False:
            time.sleep(1)


def up(cfg, vmlist, network={}, daemonize=False):
    """ Start default test infra
    """
    # signal.signal(signal.SIGINT, sigint_handler)
    hostnetwork = None
    vm_count = 0
    if network is not {}:
        hostnetwork = HostNetwork(**network)
        hostnetwork.create()
    for vm_info in vmlist:
        vm_info["config"] = cfg
        vm = VBox(**vm_info)
        # - Import base templates
        # - Create Host only network
        vm.import_box()
        hostnetwork.attach(vm)
        # Start the vm
        vm.start()
        # Host ssh config
        host_ip = "127.0.0.1"
        host_port = _firstforward_port + vm_count
        # Enable forwarding
        vm.forward_ssh(host_ip=host_ip, host_port=host_port)
        # Wait for ssh to respond
        waiting_ssh(vm)
        vm.launch_firstboot()
        vm_count += 1
        _vms.append(vm)
    if not daemonize:
        _running = True
        try:
            while _running:
                vm.getinfo()
                logger.info("{} is running with address {}"
                            .format(vm.name, vm.ip))
                _vms.append(vm)
                input("Ctrl+c to remove the infra\n\
                      Any other key to run in background")
                _running = False
                print()
        except KeyboardInterrupt:
            logger.info("Remove host network")
            down(cfg, vmlist)
            clean(cfg, vmlist)


def clean(network={}):
    """ Remove all box with name fregate
    """
    networks = HostNetwork.list(network=network)
    for hostnetwork in networks:
        hostnetwork.delete()
    vms = VBox.list()
    for vm in vms:
        if re.search('^fregate', vm['name']):
            VBox.destroy(vm['uuid'])


def down(cfg, vmlist):
    """ Stop all box
    """
    _get_vmlist(cfg, vmlist)
    for vm in _vms:
        vm.stop()


def status(cfg, vmlist):
    print()
    print(vmlist)
    _get_vmlist(cfg, vmlist)
    for vm in _vms:
        vm.getinfo()
        if vm.infos.get("VMState") == "running":
            logger.info("-"*30)
            logger.info("   {} is running".format(vm.name))
            logger.info("   Hostname   : {}".format(vm.hostname))
            logger.info("   Ip         : {}".format(vm.ip))
            logger.info("   User       : {}".format(vm.ssh_user))


def services(action, vmlist, service):
   """Services section
   """
   index = svc.index(vmlist)
   if action == 'add':
       index[service].add()
   if action == 'remove':
       index[service].remove()
   if action == 'clean':
       index[service].clean()
   if action == 'describe':
       index[service].describe()


#  def kubectl(command):
#      pass
#      #  code, output = execute(final_cmd, wait=True, stdout=True, shell=True)
#      #  print(output)
#      #  if code is 0 and int(output[0]) is 0:
#      #      return True
#      #  return False
#
