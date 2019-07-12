#!/bin/bash

# This script creates a hostname using the CPU Id
# It updates /etc/hostname and /etc/hosts files


CURRENT_HOSTNAME=$(cat /etc/hostname)

CPUID=$(awk '/Serial/ {print $3}' /proc/cpuinfo | sed 's/^0*//')
echo "Current Name" $CURRENT_HOSTNAME
echo "CPU ID" $CPUID
NEW_HOSTNAME="keycodebox-"$CPUID
echo "HOST NAME" $NEW_HOSTNAME

if [ "$NEW_HOSTNAME" != "$CURRENT_HOSTNAME" ]; then
    echo "Updating Host Name" $NEW_HOSTNAME
    echo $NEW_HOSTNAME > /etc/hostname
    sudo sed -i "/127.0.1.1/s/$CURRENT_HOSTNAME/$NEW_HOSTNAME/" /etc/hosts
fi
