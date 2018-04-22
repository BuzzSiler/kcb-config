#!/usr/bin/env bash



KCBSCRIPTS=$KCBCONFIG_ROOT/scripts
KCBBIN=$KCBCONFIG_ROOT/bin
KCBRUN=$KCBCONFIG_ROOT/run
KCBLOGS=$KCBCONFIG_ROOT/logs/stderr.log
KCBDEV=~/dev
KCBREPO=https://github.com/BuzzSiler/keycodebox-key.git
KCBDB=$KCBCONFIG_ROOT/database

KCBVNC_CREDENTIALS=$KCBCONFIG_ROOT/config/vnc_creds.txt
KCBVNC_CONF=$KCBCONFIG_ROOT/config/x11vnc.cfg

#---------------------KCB Development -----------------------
# Use the following for development only
unset KCBVNCOVERRIDE
# Uncomment to prevent the vnc server script from being run
#export KCBVNCOVERRIDE=
