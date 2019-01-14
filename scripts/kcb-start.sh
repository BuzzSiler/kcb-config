#!/usr/bin/env bash

#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

#------------------------ KCB Update -------------------------
# Handle new binary update
# Note: This approach is flawed wrt to database changes

# This was the old way
#FILE='/home/pi/bin/Alpha_NEW'
#if [ -f $FILE ];
#then
#    sudo rm -rf /usr/local/bin/alpha
#    sudo mv /home/pi/bin/Alpha_NEW /usr/local/bin/alpha
#fi
# This is a new way (untested)
NEWFILE=`ls $KCBBIN/*_NEW`
if [ -f "$NEWFILE" ];
then
    echo "Found new file" $NEWFILE
    alpha=$NEWFILE
    # root filename is *, so strip off '_NEW'
    alpha=${alpha%_NEW}
    # strip off leading path
    alpha=${alpha##*/}
    mv $NEWFILE $KCBBIN/$alpha
    $KCBSCRIPTS/kcb-link.sh $KCBBIN/$alpha
    sudo chmod +x $KCBBIN/$alpha
fi

#------------------------ KCB VNC ----------------------------
if ! pgrep -x "x11vnc" > /dev/null;
then
    echo "VNC is not running.  Starting now..."
    $KCBSCRIPTS/kcb-remotedesktop.sh
else
    echo "VNC is running"
fi

#----------------------- KCB Launch --------------------------
$KCBSCRIPTS/kcb-launch.sh
