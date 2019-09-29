#!/usr/bin/env bash

# Turn off display power
# Application will turn it back on
#vcgencmd display_power 0

#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

#------------------------  KCB Name  ------------------------
sudo $KCBSCRIPTS/kcb-hostname.sh

#------------------------ KCB Update -------------------------
# Handle new binary update

NEWFILE=`ls $KCBBIN/*_NEW`
if [ -f "$NEWFILE" ];
then
    echo "Found new file" $NEWFILE
    alpha=$NEWFILE
    # root filename is *, so strip off '_NEW'
    alpha=${alpha%_NEW}
    # strip off leading path
    alpha=${alpha##*/}
    mv -f $NEWFILE $KCBBIN/$alpha
    $KCBSCRIPTS/kcb-link.sh $KCBBIN/$alpha
    sudo chmod +x $KCBBIN/$alpha
fi

#------------------------ KCB VNC ----------------------------
#if ! pgrep -x "x11vnc" > /dev/null;
#then
#    echo "VNC is not running.  Starting now..."
#    $KCBSCRIPTS/kcb-remotedesktop.sh
#else
#    echo "VNC is running"
#fi

#----------------------- KCB Launch --------------------------
$KCBSCRIPTS/kcb-launch.sh
