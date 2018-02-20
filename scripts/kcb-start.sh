#!/usr/bin/env bash

source $KCBCONFIG

# Allow kcb to started without starting the vncserver
# Default, as called from .bashrc, is to start vncserver

if [ "$1" != "--novnc" ]; then
    $KCBSCRIPTS/kcb-remotedesktop.sh
fi

$KCBSCRIPTS/kcb-launch.sh
