#!/usr/bin/env bash

source $KCBCONFIG
hiddev=$(/home/pi/kcb-config/scripts/kcb-getjsonvalue.sh /home/pi/kcb-config/settings/fleetwave.json hidDevice)

if pgrep -x "pcsc_scan" > /dev/null
then
    echo "pcsc scan is running"
else
    if [[ $hiddev == *"5427-SC"* ]];
    then
        echo "SmartCard HID Device enabled"
        pcsc_scan -n &> /home/pi/kcb-config/logs/pcscscan.log &
    fi
fi
sudo alpha -nograb -style motif &> $KCBLOGS
#sudo alpha -nograb &> $KCBLOGS
