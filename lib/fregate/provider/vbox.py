# coding: utf-8
# =============================================================================
# Name     : vbox.py
# Function : VirtualBox CLI Wrapper
#            Basic functionnalty like up/down/destroy/ssh
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


from __future__ import absolute_import
import os
import re
import logging
import subprocess
from urllib.parse import urlparse
from urllib.request import urlopen
from jinja2 import Template
from lib.fregate.commons.utils import fatal
from lib.fregate.commons.shell import execute

BOX_FOLDER = "boxes"


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
        self.name = self.hostname
        self.box_network = None
        self.forwarding_enabled = False
        self.ssh_privkey = config["ssh"]["privkey"]
        self.ssh_user = config["ssh"]["user"]
        self.ssh_port = config["ssh"]["port"]
        self.logger = logging.getLogger(name=self.hostname)

    def get_sshcmd(self, forwarding=False, scp=False, target=None, dest=None):
        """ The getter for the ssh shell command line with all required params
            @fowarding       Get the ssh cmd when the forwarding mode
                             of this module is enabled
            @scp             Get and scp command instead of ssh
                             When scp mode is enabled you
                             need to specify target and destination
            @target          The file on you host to transfer
                             or a directory/file from the guest
            @dest            Remote dest on the guest or a
                             directory/file on your host
            @docker socket  Get the ssh cmd to forward docker socket
                            usage: [dest, src]
        """
        ssh_command = "scp" if scp else "ssh"
        ssh_port = "-P" if scp else "-p"

        if forwarding:
            self.logger.debug("Connect to ssh with forwarding")
            ssh_ip = "127.0.0.1"
            ssh_port += " {}".format(self.forwared_port)
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
        """ Enable ssh forwarding between vm to host
            The ssh port of the guest will be forward to the specify host port
        """
        code = execute(["vboxmanage", "controlvm", self.name,
                        "natpf2", "guestssh,tcp,{},{},,{}"
                        .format(host_ip, host_port, guest_port)])
        if code is not 0:
            fatal("Failed to enable ssh forwarding")
        else:
            self.logger.info("Enable forwarding")
            self.logger.info("{}:{} > {}:{}"
                             .format(host_ip, host_port,
                                     self.name, guest_port))
            self.forwarding_enabled = True
            self.forwared_port = host_port
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
            self.logger.warning("Failed to copy firstboot script {}"
                                .format(script_path))
        else:
            self.logger.debug("Success copy {}".format(script_path))
        return code

    def launch_firstboot(self, script="scripts/firstboot.sh.tpl", **kwargs):
        """ Template a firstboot script to update network configs and install
            dependencies.
            Copy firstboot template to vm and execute the script
            **kwargs will be replace in jinja2 template rendering as follow
            **kwargs=(VM_IP="192.168.5.1")
            firstboot template file
            => "{{ VM_IP }}" => 192.168.5.1
            @return 0 on success execute
        """
        try:
            with open(script) as f:
                t = Template(f.read())
                firstboot_script = t.render(
                    kwargs,
                    VM_IP=self.ip,
                    VM_NETMASK=self.netmask,
                    VM_NETWORK=self.network,
                    VM_HOSTNAME=self.hostname,
                )
                f.close()
            self.logger.info("Success read template {}".format(script))
        except Exception as e:
            fatal("Failed to open {}".format(script), exception=e)
        else:
            firstboot_path = '/tmp/{}.firstboot.sh'.format(self.hostname)
            self.logger.info("Launch firstboot on {}".format(self.hostname))
            with open(firstboot_path, 'w+') as f:
                f.write(firstboot_script)
            success_copy = self.copy_firstboot(firstboot_path)
            if success_copy:
                return -1
            ssh_command = self.get_sshcmd(forwarding=self.forwarding_enabled)
            ssh_command += " sh {}".format(firstboot_path)
            code = execute(ssh_command, wait=True, shell=True)
            if code is not 0:
                self.logger.warning("Failed to execute firstboot script {}"
                                    .format(firstboot_script))
                return -1
            self.logger.info("firstboot.sh successfully executed")
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
            self.logger.warning("Failed to retrieve infos of {}"
                                .format(self.name))
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

    def download_box(self):
        try:
            parsed_url = urlparse(self.box_url)
            if parsed_url.scheme in ['http', 'https']:
                self.logger.info("Downloading box : {}"
                                 .format(parsed_url.geturl()))
                with open(self.box_path, 'wb+') as f:
                    self.logger.info(self.box_path)
                    response = urlopen(parsed_url.geturl())
                    data = response.read()
                    f.write(data)
                    f.close()
        except Exception as e:
            fatal("Failed to open {}".format(self.box_path), exception=e)
        else:
            self.logger.info("Download finished")

    def rename(self, target, new_name):
        code = execute(["vboxmanage", "modifyvm", target, "--name", new_name])
        if code is not 0:
            self.logger.warning("Failed to rename box {}".format(target))
        else:
            self.logger.info("Rename box {} => {}".format(target, new_name))
            self.name = new_name
        return code

    def import_box(self):
        """ @params box_url box .ova url
            Import a .ova from url
        """
        parsed_url = urlparse(self.box_url)
        if parsed_url.scheme in ['http', 'https']:
            self.box_path = BOX_FOLDER + parsed_url.path
            if not os.path.exists(self.box_path):
                self.logger.info("{} doest not exists".format(self.box_path))
                self.download_box()
            self.logger.info("Importing {}".format(self.box_path))
        code, output = execute(["vboxmanage", "import", self.box_path],
                               stdout=True)
        if code is not 0:
            fatal("Failed to import {}".format(self.box_url))
        else:
            for line in output:
                if line is not None:
                    vm_name = re.search('".+"', line)
                    if re.search("VM name", line) and vm_name is not None:
                        vm_name = re.sub('"', '', vm_name.group(0))
                        self.logger.debug("VM {} is imported"
                                          .format(vm_name))
                        return self.rename(vm_name, self.hostname)
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
            self.logger.debug("VM {} is created".format(self.name))
            return vm_path

    def delete(self):
        """ @params name <vm name|uuid>
            Delete the vm
        """
        code = execute(["vboxmanage", "unregistervm", self.name, "--delete"])
        if code is not 0:
            fatal("Failed to delete {}".format(self.name))
        else:
            self.logger.debug("VM {} is removed".format(self.name))
        return 0

    def start(self, mode='headless', env={}):
        """ @params name <vm name|uuid>
            Start the vm
        """
        command = ["vboxmanage", "startvm", self.name, "--type", mode]
        # Not working like we want
        # if len(env.keys()) is not 0:
        #     for key in env.keys():
        #         self.logger.debug("ENV {}={}".format(key, env[key]))
        #         command.append("-E")
        #         command.append('{}="{}"'.format(key, env[key]))
        code = execute(command)
        if code is not 0:
            fatal("Failed to start {}".format(self.name))
        else:
            self.logger.debug("VM {} is starting".format(self.name))
        return 0

    def stop(self):
        """ @params name <vm name|uuid>
            Stop the vm
        """
        code, output = execute([
            "vboxmanage", "controlvm", self.name, "poweroff"
        ], stdout=True)
        if code is not 0:
            fatal("Failed to stop {}".format(self.name))
        else:
            self.logger.debug("VM {} stopped".format(self.name))
        return 0
