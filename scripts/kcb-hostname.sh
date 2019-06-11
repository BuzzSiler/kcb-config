#!/bin/bash
# script to set Pi hostname based on MAC (or Serial number)
# 2017-08-18
# This script should be run as root (or with sudo) to change names
# If run by a user it will report changes, but will NOT implement them
# Works for PiB (all models), Pi2, Pi3, PiZeroW with on board networking
# PiA models will set a unique Name based on Serial number

PDIR="$(dirname "$0")"  # directory containing script
CURRENT_HOSTNAME=$(cat /etc/hostname)
# Find MAC of eth0, or if not exist wlan0
if [ -e /sys/class/net/eth0 ]; then
    MAC=$(cat /sys/class/net/eth0/address)
elif [ -e /sys/class/net/enx* ]; then
    MAC=$(cat /sys/class/net/enx*/address)
else
    MAC=$(cat /sys/class/net/wlan0/address)
fi

# NOTE the last 6 bytes of MAC and CPUID are identical
CPUID=$(awk '/Serial/ {print $3}' /proc/cpuinfo | sed 's/^0*//')
echo "Current Name" $CURRENT_HOSTNAME
echo "MAC" $MAC
# If you want to specify hostnames create a file PiNames.txt with MAC hostname list e.g.
# b8:27:eb:01:02:03 MyPi
# If not found a unique Name based on Serial number will be set
NEW_HOSTNAME=$(awk /$MAC/' {print $2}' $PDIR"/PiNames.txt")
echo "Name found" $NEW_HOSTNAME
if [ "$NEW_HOSTNAME" == "" ]; then
    NEW_HOSTNAME="keycodebox-"$CPUID
fi

if [ $NEW_HOSTNAME == $CURRENT_HOSTNAME ]; then
    echo "Name already set"
else
    echo "Setting Name" $NEW_HOSTNAME
    echo $NEW_HOSTNAME > /etc/hostname
    sed -i "/127.0.1.1/s/$CURRENT_HOSTNAME/$NEW_HOSTNAME/" /etc/hosts
fi