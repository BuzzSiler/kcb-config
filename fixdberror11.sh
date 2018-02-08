#!/usr/bin/env bash

# Inputs
#   $1 - the database

sqlite3 $1 "pragma integrity_check"

. execdbcmds.sh $1 fixdberror11_p1.txt

sqlite3 fixed_$1

. execdbcmds.sh fixdberror11_p2.txt

mv $1 corrupt_$1
mv fixed_$1 $1
