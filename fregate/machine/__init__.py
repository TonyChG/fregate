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
import subprocess
from commons.utils import fatal


def update_hostnetwork(vm_name, net_name):
    """ @params vm_name Machine name or uuid
        @params net_name Hostonly network name
    """
    try:
        subprocess.call([
            "vboxmanage", "modifyvm", vm_name,
            "--hostonlyadapter1", net_name
        ])
        subprocess.call([
            "vboxmanage", "modifyvm", vm_name,
            "--nic1", "hostonly"
        ])
    except Exception as e:
        fatal("Failed to attach host only network", exception=e)
    else:
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
                "vboxmanage", "hostonlyif",
                "ipconfig", net_name,
                "--ip", ip
            ])
    except Exception as e:
        fatal("Failed to create new host only network", exception=e)
    else:
        return net_name


def import_box(box_url):
    """ @params box_url box .ova url
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
                    return vm_name
        return vm_name


def create(name):
    """ @params name <vm name|uuid>
    """
    try:
        new_vm = subprocess.check_output([
            "vboxmanage", "createvm",
            "--name", name,
            "--ostype", "Linux26_64",
            "--register"
        ])
    except Exception as e:
        fatal("Impossible to create the new node", exception=e)
    else:
        vm_info = new_vm.decode('utf-8').split('\n')
        for l in vm_info:
            vm_path = re.search("'/.+'", l)
            if vm_path is not None:
                print(vm_path.group(0))
        return vm_path


def list_vm():
    """ @return vm list (uuid, name)
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
    """
    try:
        status = subprocess.call([
            "vboxmanage", "unregistervm",
            name, "--delete"
        ])
    except Exception as e:
        fatal("Failed to delete {}".format(name), exception=e)
    else:
        return status


def start(name):
    try:
        subprocess.call([
            "vboxmanage", "startvm", name, "--type", "gui"
        ])
    except Exception as e:
        fatal("Failed to start {}".format(name), exception=e)
    else:
        return True


def stop(name):
    pass
