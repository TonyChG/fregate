#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : create.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import re
import logging
import subprocess
from commons.utils import fatal
from commons.shell import execute


class VBox:
    @staticmethod
    def list():
        """ @return vm list (uuid, name)
            List all virtualbox vm
        """
        vms_list = []
        code, output = execute(["vboxmanage", "list", "vms"], stdout=True)
        if code is not 0:
            fatal("Cannot fetch vm list")
        for vm in output:
            if vm != '':
                vm_name = re.search('".+"', vm)
                vm_uuid = re.search('{.+}', vm)
                if vm_name is not None and vm_uuid is not None:
                    vm_uuid = re.sub(r'({|})', "", vm_uuid.group(0))
                    vm_name = re.sub(r'"', "", vm_name.group(0))
                    vms_list.append({"uuid": vm_uuid, "name": vm_name})
        return vms_list

    @staticmethod
    def destroy(id):
        """ @params name <vm name|uuid>
            Delete the vm
        """
        code = execute(["vboxmanage", "unregistervm", id, "--delete"])
        if code is not 0:
            fatal("Failed to delete {}".format(id))
        else:
            logging.debug("VM {} is removed".format(id))
        return 0

    def __init__(self, box_url=None, ip=None, network=None, netmask=None,
                 hostname=None):
        self.box_url = box_url
        self.hostname = hostname
        self.ip = ip
        self.network = network
        self.netmask = netmask
        self.infos = {}
        self.name = None
        self.box_network = None

    def ssh(self, identity_file=None, user=None):
        subprocess.call("ssh -o 'StrictHostKeyChecking=no' -i {} {}@{}"
                        .format(identity_file, user, self.ip),
                        shell=True)

    def getinfo(self):
        """ @params vm_name Virtualbox VM name
        """
        code, output = execute([
            "vboxmanage", "showvminfo", self.name, "--machinereadable"
        ], stdout=True)
        if code is not 0:
            fatal("Failed to retrieve infos of {}".format(self.name))
        else:
            for info in output:
                if info is not None:
                    splited_line = info.split('=')
                    if len(splited_line) == 2 \
                            and splited_line[0] != '' \
                            and splited_line[1] != '':
                        value = re.sub('"', '', splited_line[1])
                        self.infos[splited_line[0]] = value
            return self.infos

    def import_box(self):
        """ @params box_url box .ova url
            Import a .ova from url
        """
        code, output = execute(["vboxmanage", "import", self.box_url],
                               stdout=True)
        if code is not 0:
            fatal("Failed to import {}".format(self.box_url))
        else:
            for line in output:
                if line is not None:
                    vm_name = re.search('".+"', line)
                    if re.search("VM name", line) and vm_name is not None:
                        self.name = re.sub('"', '', vm_name.group(0))
                        logging.debug("VM {} is imported".format(self.name))
                        return 0
        return -1

    def create(self):
        """ @params name <vm name|uuid>
            Create a new vm
        """
        code, output = execute([
            "vboxmanage", "createvm", "--name", self.name,
            "--ostype", "Linux26_64", "--register"
        ], stdout=True)
        if code is not 0:
            fatal("Impossible to create the new node")
        else:
            for line in output:
                vm_path = re.search("'/.+'", line)
                if vm_path is not None:
                    print(vm_path.group(0))
            logging.debug("VM {} is created".format(self.name))
            return vm_path

    def delete(self):
        """ @params name <vm name|uuid>
            Delete the vm
        """
        code = execute(["vboxmanage", "unregistervm", self.name, "--delete"])
        if code is not 0:
            fatal("Failed to delete {}".format(self.name))
        else:
            logging.debug("VM {} is removed".format(self.name))
        return 0

    def start(self, mode='headless', env={}):
        """ @params name <vm name|uuid>
            Start the vm
        """
        command = ["vboxmanage", "startvm", self.name, "--type", mode]
        if len(env.keys()) is not 0:
            for key in env.keys():
                logging.debug("ENV {}={}".format(key, env[key]))
                command.append("-E")
                command.append('{}="{}"'.format(key, env[key]))
        code = execute(command)
        if code is not 0:
            fatal("Failed to start {}".format(self.name))
        else:
            logging.debug("VM {} is starting".format(self.name))
        return 0

    def stop(self):
        """ @params name <vm name|uuid>
            Stop the vm
        """
        code = execute([
            "vboxmanage", "controlvm", self.name, "poweroff"
        ], stdout=False)
        if code is not 0:
            fatal("Failed to stop {}".format(self.name))
        else:
            logging.debug("Stop VM {}".format(self.name))
        return 0
