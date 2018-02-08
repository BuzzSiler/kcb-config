#!/usr/bin/env bash

# Inputs
#    $1 - the database
#    $2 - a file containing dot commands

sqlite3 $1 ".read $2"

# EOF
