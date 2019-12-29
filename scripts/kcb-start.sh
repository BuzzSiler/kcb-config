#!/usr/bin/env bash


#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

#-----------------------  Log Rotate ------------------------
$KCBSCRIPTS/kcb-logrotate.sh

#------------------------  KCB Name  ------------------------
sudo $KCBSCRIPTS/kcb-hostname.sh

#------------------------ KCB Update ------------------------
$KCBSCRIPTS/kcb-update.sh


#----------------------- KCB Launch -------------------------
$KCBSCRIPTS/kcb-launch.sh

#------------------------------------------------------------
# EOF
