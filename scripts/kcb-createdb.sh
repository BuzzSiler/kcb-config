#!/usr/bin/env bash

source $KCBCONFIG
DBPATH=/home/pi/run


if [ "$1" == "" ]; then
    echo "No schema provided"
    exit
fi

# Copy the existing database to a backup
now=`date '+%Y_%m_%d__%H_%M_%S'`
mv $DBPATH/Alpha.db $DBPATH/Alpha-$now.db

schema=$1
actions=$2

# Execute sqlite3 command to create empty database from schema file
if [ "$schema" == "0.1" ]; then
    echo "$schema is not supported"
    #sqlite3 $DBPATH/Alpha.db < $KCBDB/kcb-v0.1.schema.sql
elif [ "$schema" == "0.2" ]; then
    echo "$schema is not supported"
    #sqlite3 $DBPATH/Alpha.db < $KCBDB/kcb-v0.2.schema.sql
elif [ "$schema" == "0.3" ]; then
    echo "$schema is supported"
    sqlite3 $DBPATH/Alpha.db < $KCBDB/kcb-v0.3.default.sql
fi

if [ "$actions" == "default" ]; then
    echo "Inserting default admin values"
    ###sqlite3 $DBPATH/Alpha.db < $KCBDB/admin-default.sql
elif [ "$actions" == "test" ]; then
    echo "Inserting test codes"
fi
