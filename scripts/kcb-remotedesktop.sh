#!/usr/bin/env bash

#source $KCBCONFIG

#ps aux | grep autoport | cut -d' ' -f8 | xargs kill -9 &
#ps aux | grep autoport | cut -d' ' -f9 | xargs kill -9 &
#sleep 1
#vncport="$(cat $KCBVNC_CREDENTIALS  | cut -d'|' -f2 | cut -d' ' -f1)"
#vncpass="$(cat $KCBVNC_CREDENTIALS  | cut -d'|' -f2 | cut -d' ' -f2)"
#x11vnc -storepasswd $vncpass "$KCBVNC_CONF"
#sleep 1
#x11vnc -bg -forever -autoport 5901 -rfbauth /home/pi/kcb-config/config/x11vnc.cfg -o /home/pi/kcb-config/logs/x11vnc.log
