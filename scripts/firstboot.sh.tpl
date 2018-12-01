#!/bin/sh
# =============================================================================
# Name     : firstboot.sh
# Function : This script is template with jinja2
#            and launch on firstboot of the vm
# Usage    : ./firstboot.sh
# Version  : 1.0.0
# vi       : set expandtab shiftwidth=4 softtabstop=4
# =============================================================================

set -ex

apk add --no-cache -q rsync bash

sed -i 's/ash/bash/g' /etc/passwd

echo "{{ VM_HOSTNAME }}" > /etc/hostname
hostname -F /etc/hostname

cat > /etc/hosts <<EOF
127.0.0.1       {{ VM_HOSTNAME }} localhost.localdomain localhost
::1             localhost localhost.localdomain
EOF

# Fixing error / is already mounted on rke up
mount --make-rshared /

# Network configuration
cat > /etc/network/interfaces <<EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
        address {{ VM_IP }}
        netmask {{ VM_NETMASK }}
        network {{ VM_NETWORK }}

auto eth1
iface eth1 inet dhcp
EOF

service networking restart && exit 0
