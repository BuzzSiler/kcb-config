#!/usr/bin/env bash


#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

#------------------------  KCB Name  ------------------------
sudo $KCBSCRIPTS/kcb-hostname.sh

#------------------------ KCB Update -------------------------
$KCBSCRIPTS/kcb-update.sh

#----------------------- PCSC SCAN ---------------------------
$KCBSCRIPTS/kcb-pcscscan.sh

#----------------------- KCB Launch --------------------------
$KCBSCRIPTS/kcb-launch.sh
