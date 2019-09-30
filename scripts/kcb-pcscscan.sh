#!/usr/bin/env bash

source $KCBCONFIG
hiddev=$($KCBSCRIPTS/kcb-getjsonvalue.sh $KCBSETTINGS/fleetwave.json hidDevice)

if pgrep -x "pcsc_scan" > /dev/null
then
    echo "pcsc scan is running"
else
    if [[ $hiddev == *"5427-SC"* ]];
    then
        echo "SmartCard HID Device enabled"
        pcsc_scan -n &> $KCBLOGS/pcscscan.log &
    fi
fi

