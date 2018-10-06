#!/usr/bin/env bash

source $KCBCONFIG
if pgrep -x "pcsc_scan" > /dev/null
then
    echo "pcsc scan is running"
else
    pcsc_scan &
fi
sudo alpha -nograb -style motif &> $KCBLOGS
