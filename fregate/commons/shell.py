#!/usr/bin/env python3
# coding: utf-8
# =============================================================================
# Name     : shell.py
# Function :
# Usage    :
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================


# from utils import fatal
import subprocess
import logging


def execute(commandline, stdout=False):
    returncode = -1
    try:
        with subprocess.Popen(commandline,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE) as proc:
            returncode = proc.wait()
            if returncode is not 0:
                raise Exception("{} failed".format(commandline))
            output = proc.stdout.read()
            if len(output) > 0:
                output = output.decode('utf-8')[:-1]
                output = output.split('\n')
    except Exception as e:
        logging.debug(e)
        return -1
    else:
        if stdout is False:
            return returncode
        return returncode, output


if __name__ == '__main__':
    code, output = execute(["vboxmanage", "list", "vms"], stdout=True)
    for line in output:
        print(line)
