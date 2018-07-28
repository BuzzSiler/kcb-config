#!/usr/bin/env bash

#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

#---------------------KCB Development -----------------------
# Use the following for development only
#unset KCBVNCOVERRIDE
# Uncomment to prevent the vnc server script from being run
#export KCBVNCOVERRIDE=

# Allow kcb to be started without starting the vncserver
# Default, as called from .bashrc, is to start vncserver
# Setting the variable KCBVNCOVERRIDE will prevent vncserver
# from being started in an SSH session.

#------------------------ KCB VNC ----------------------------
if [ ! -v KCBVNCOVERRIDE ]; then
    $KCBSCRIPTS/kcb-remotedesktop.sh
fi

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
    alpha=$NEWFILE
    # root filename is *, so strip off '_NEW'
    alpha=${alpha%_NEW}
    alpha=${alpha##*/}
    mv $NEWFILE $KCBBIN/$alpha
    sudo chmod +x $KCBBIN/$alpha
    $KCBSCRIPTS/kcb-link.sh $KCBBIN/$alpha
fi

#----------------------- KCB Launch --------------------------
$KCBSCRIPTS/kcb-launch.sh
