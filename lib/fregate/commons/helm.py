#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : helm.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

from subprocess import call

def helm(commands, vm):
    ssh_cmd = vm.get_sshcmd(scp=False)
    base_cmd = " "
    for command in commands:
        command = ' '.join(command)
        base_cmd += "/usr/bin/helm {}; ".format(command)
    print(base_cmd)
    final_cmd = ssh_cmd + base_cmd
    call(final_cmd, shell=True)

