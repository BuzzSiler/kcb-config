ps aux | grep autoport | cut -d' ' -f8 | xargs kill -9 &
ps aux | grep autoport | cut -d' ' -f9 | xargs kill -9 &
sleep 1
vncport="$(cat /home/pi/run/vnc_creds.txt  | cut -d'|' -f2 | cut -d' ' -f1)"
vncpass="$(cat /home/pi/run/vnc_creds.txt  | cut -d'|' -f2 | cut -d' ' -f2)"
x11vnc -storepasswd $vncpass "/home/pi/etc/x11vnc.cfg"
sleep 1
x11vnc -bg -forever -autoport $vncport -rfbauth "/home/pi/etc/x11vnc.cfg"
