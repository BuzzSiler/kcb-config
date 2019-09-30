#!/usr/bin/env bash

source $KCBCONFIG
sudo alpha -nograb -style motif &> $KCBLOGS/stderr.log
