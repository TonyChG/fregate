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


def get_vmstate(vm_name):
    """ @params vm_name Virtualbox VM name
    """
    try:
        vm_info = subprocess.check_output([
            "vboxmanage", "showvminfo", vm_name, "--machinereadable"
        ])
    except Exception as e:
        fatal("Failed to retrieve infos of {}".format(vm_name), exception=e)
    else:
        infos = {}
        for info in vm_info.decode('utf-8').split('\n'):
            if info is not None:
                splited_line = info.split('=')
                if len(splited_line) == 2 \
                        and splited_line[0] != '' \
                        and splited_line[1] != '':
                    value = re.sub('"', '', splited_line[1])
                    infos[splited_line[0]] = value
        return infos


def delete_hostnetwork(net_name):
    """ @params net_name Virtualbox HostOnlyNetwork name
    """
    try:
        subprocess.check_output([
            "vboxmanage", "hostonlyif", "remove", net_name
        ])
    except Exception as e:
        fatal("Failed to delete new host only network", exception=e)
    else:
        logging.debug("Network {} is deleted".format(net_name))
        return 0


def update_hostnetwork(vm_name, net_name):
    """ @params vm_name Machine name or uuid
        @params net_name Hostonly network name
    """
    try:
        subprocess.call([
            "vboxmanage", "modifyvm", vm_name, "--hostonlyadapter1", net_name
        ])
        subprocess.call([
            "vboxmanage", "modifyvm", vm_name, "--nic1", "hostonly"
        ])
    except Exception as e:
        fatal("Failed to attach host only network", exception=e)
    else:
        logging.debug("Sucessfully attached {} to {}"
                      .format(net_name, vm_name))
        return 0


def create_network(ip, netmask):
    """ @params ip hostonly network ip
        @params netmask hostonly network mask
    """
    try:
        output = subprocess.check_output([
            "vboxmanage", "hostonlyif", "create"
        ])
        net_name = re.search("'.+'", output.decode('utf-8'))
        if net_name is not None:
            net_name = re.sub("'", '', net_name.group(0))
            subprocess.check_output([
                "vboxmanage", "hostonlyif", "ipconfig", net_name, "--ip", ip
            ])
    except Exception as e:
        fatal("Failed to create new host only network", exception=e)
    else:
        logging.debug("Network {} is created".format(net_name))
        return net_name


def import_box(box_url):
    """ @params box_url box .ova url
        Import a .ova from url
    """
    try:
        new_vm = subprocess.check_output([
            "vboxmanage", "import", box_url
        ])
    except Exception as e:
        fatal("Failed to import {}".format(box_url), exception=e)
    else:
        vm_name = ""
        for l in new_vm.decode('utf-8').split('\n'):
            if l is not None:
                vm_name = re.search('".+"', l)
                if re.search("VM name", l) and vm_name is not None:
                    vm_name = re.sub('"', '', vm_name.group(0))
                    logging.debug("VM {} is imported".format(vm_name))
                    return vm_name
        return vm_name


def create(name):
    """ @params name <vm name|uuid>
        Create a new vm
    """
    try:
        new_vm = subprocess.check_output([
            "vboxmanage", "createvm", "--name", name,
            "--ostype", "Linux26_64", "--register"
        ])
    except Exception as e:
        fatal("Impossible to create the new node", exception=e)
    else:
        vm_info = new_vm.decode('utf-8').split('\n')
        for l in vm_info:
            vm_path = re.search("'/.+'", l)
            if vm_path is not None:
                print(vm_path.group(0))
        logging.debug("VM {} is created".format(name))
        return vm_path


def list_vm():
    """ @return vm list (uuid, name)
        List all virtualbox vm
    """
    try:
        vms = subprocess.check_output(["vboxmanage", "list", "vms"])
        vms_list = []
    except Exception as e:
        fatal("Cannot fetch vm list", exception=e)
    else:
        for vm in vms.decode('utf-8').split('\n'):
            if vm != '':
                vm_name = re.search('".+"', vm)
                vm_uuid = re.search('{.+}', vm)
                if vm_name is not None and vm_uuid is not None:
                    vm_uuid = re.sub(r'({|})', "", vm_uuid.group(0))
                    vm_name = re.sub(r'"', "", vm_name.group(0))
                    vms_list.append({"uuid": vm_uuid, "name": vm_name})
    return vms_list


def delete(name):
    """ @params name <vm name|uuid>
        Delete the vm
    """
    try:
        status = subprocess.call([
            "vboxmanage", "unregistervm", name, "--delete"
        ])
    except Exception as e:
        fatal("Failed to delete {}".format(name), exception=e)
    else:
        logging.debug("VM {} is removed".format(name))
        return status


def start(name, env={}):
    """ @params name <vm name|uuid>
        Start the vm
    """
    try:
        command = ["vboxmanage", "startvm", name, "--type", "gui"]
        if len(env.keys()) is not 0:
            for key in env.keys():
                logging.debug("ENV {}={}".format(key, env[key]))
                command.append("-E")
                command.append('{}="{}"'.format(key, env[key]))
        subprocess.call(command)
    except Exception as e:
        fatal("Failed to start {}".format(name), exception=e)
    else:
        logging.debug("VM {} is starting".format(name))
        return True


def stop(name):
    """ @params name <vm name|uuid>
        Stop the vm
    """
    try:
        subprocess.call([
            "vboxmanage", "controlvm", name, "poweroff"
        ])
    except Exception as e:
        fatal("Failed to stop {}".format(name), exception=e)
    else:
        logging.debug("Stop VM {}".format(name))
        return True
