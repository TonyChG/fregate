#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : vbox.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


import re
import logging
import subprocess
from jinja2 import Template
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
    def force_stop(vm_uuid):
        """ @params name <vm name|uuid>
            Forcing shutdown of the vm
        """
        code = execute([
            "vboxmanage", "controlvm", vm_uuid, "poweroff"
        ], stdout=False)
        if code is not 0:
            fatal("Failed to stop {}".format(vm_uuid))
        else:
            logging.debug("Stop VM {}".format(vm_uuid))
        return 0

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

    def __init__(self, id=None, box_url=None, ip=None, network=None,
                 netmask=None, hostname=None):
        self.box_url = box_url
        self.hostname = hostname
        self.id = id
        self.ip = ip
        self.network = network
        self.netmask = netmask
        self.infos = {}
        self.name = None
        self.box_network = None
        self.ssh_enabled = False

    def forward_ssh(self, host_ip="127.0.0.1", host_port=2222, guest_port=22):
        code = execute(["vboxmanage", "controlvm", self.name,
                        "natpf2", "guestssh,tcp,{},{},,{}"
                        .format(host_ip, host_port, guest_port)])
        if code is not 0:
            fatal("Failed to enable ssh forwarding")
        else:
            logging.info("Enable forwarding")
            logging.info("{}:{} > {}:{}"
                         .format(host_ip, host_port, self.name, guest_port))
            self.ssh_enabled = True
            return 0

    def launch_firstboot(self, script="scripts/firstboot.sh.tpl", **kwargs):
        try:
            with open(script) as f:
                t = Template(f.read())
                firstboot_script = t.render(
                    VM_IP=self.ip,
                    VM_NETMASK=self.netmask,
                    VM_NETWORK=self.network,
                    VM_HOSTNAME=self.hostname
                )
                f.close()
            logging.info("Success read template {}".format(script))
        except Exception as e:
            fatal("Failed to open {}".format(script), exception=e)
        else:
            logging.info("Launch firstboot on {}".format(self.hostname))
            ssh_params = "-o 'StrictHostKeyChecking=no'"
            ssh_params += " -q -i {}".format(".fregate.d/id_rsa", 2222)
            firstboot_path = '/tmp/{}.firstboot.sh'.format(self.hostname)
            with open(firstboot_path, 'w+') as f:
                f.write(firstboot_script)
            scp_command = "scp {} -P {} {} {}@{}:/tmp"\
                .format(ssh_params, 2222, firstboot_path, 'root', '127.0.0.1')
            code = execute(scp_command, wait=True, shell=True)
            if code is not 0:
                logging.warning("Failed to copy firstboot script {}"
                                .format(firstboot_path))
            ssh_command = "ssh {} -p {} {}@{} sh '{}'"\
                .format(ssh_params, 2222, 'root', '127.0.0.1', firstboot_path)
            code = execute(ssh_command, wait=True, shell=True)
            if code is not 0:
                logging.warning("Failed to execute firstboot script {}"
                                .format(firstboot_script))

    def ssh(self, identity_file=None, user=None):
        if self.ssh_enabled:
            logging.debug("Connect to ssh with forwarding")
            ssh_ip = "127.0.0.1"
            ssh_port = 2222
        else:
            ssh_ip = self.ip
            ssh_port = 22
        ssh_command = "ssh -p {} -o 'StrictHostKeyChecking=no' -i {} {}@{}"\
            .format(ssh_port, identity_file, user, ssh_ip)
        subprocess.call(ssh_command, shell=True)

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
