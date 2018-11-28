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
                 netmask=None, hostname=None, config={}):
        self.box_url = box_url
        self.hostname = hostname
        self.id = id
        self.ip = ip
        self.network = network
        self.netmask = netmask
        self.infos = {}
        self.name = None
        self.box_network = None
        self.forwarding_enabled = False
        self.ssh_privkey = config["ssh"]["privkey"]
        self.ssh_user = config["ssh"]["user"]
        self.ssh_port = config["ssh"]["port"]

    def get_sshcmd(self, forwarding=False, scp=False, target=None, dest=None):
        ssh_command = "scp" if scp else "ssh"
        ssh_port = "-P" if scp else "-p"

        if forwarding:
            logging.debug("Connect to ssh with forwarding")
            ssh_ip = "127.0.0.1"
            ssh_port += " {}".format(2222)
        else:
            ssh_ip = self.ip
            ssh_port += " {}".format(self.ssh_port)
        if scp and target is not None and dest is not None:
            ssh_command = "{} {} -o 'StrictHostKeyChecking=no' -i {} {} {}"\
                .format(ssh_command, ssh_port, self.ssh_privkey, target, dest)
        elif scp is False:
            ssh_command = "{} {} -o 'StrictHostKeyChecking=no' -i {} {}@{}"\
                .format(ssh_command, ssh_port, self.ssh_privkey, self.ssh_user,
                        ssh_ip)
        else:
            fatal("When using get_sshcmd in scp mode you have"
                  " to specify target and destination")
        return ssh_command

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
            self.forwarding_enabled = True
            return 0

    def copy_firstboot(self, script_path):
        dest = "{}@{}:{}".format(self.ssh_user, '127.0.0.1', script_path)
        scp_command = self.get_sshcmd(
            forwarding=self.forwarding_enabled,
            scp=True,
            target=script_path,
            dest=dest
        )
        code = execute(scp_command, wait=True, shell=True)
        if code is not 0:
            logging.warning("Failed to copy firstboot script {}"
                            .format(script_path))
        else:
            logging.debug("Success copy {}".format(script_path))
        return code

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
            firstboot_path = '/tmp/{}.firstboot.sh'.format(self.hostname)
            logging.info("Launch firstboot on {}".format(self.hostname))
            with open(firstboot_path, 'w+') as f:
                f.write(firstboot_script)
            success_copy = self.copy_firstboot(firstboot_path)
            if success_copy:
                return -1
            ssh_command = self.get_sshcmd(forwarding=self.forwarding_enabled)
            ssh_command += " sh {}".format(firstboot_path)
            code = execute(ssh_command, wait=True, shell=True)
            if code is not 0:
                logging.warning("Failed to execute firstboot script {}"
                                .format(firstboot_script))
                return -1
            logging.info("firstboot.sh successfully executed")
            return 0

    def ssh(self, identity_file=None, user=None):
        ssh_command = self.get_sshcmd(forwarding=self.forwarding_enabled)
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