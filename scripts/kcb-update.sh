#!/usr/bin/env bash


#-------------------- KCB Configuration ---------------------
# Point to the kcb configuration file and source it

source $KCBCONFIG

# Handle new binary update

NEWFILE=`ls $KCBBIN/*_NEW 2> /dev/null`
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

