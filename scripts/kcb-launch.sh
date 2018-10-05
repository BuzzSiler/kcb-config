#!/usr/bin/env bash

source $KCBCONFIG
pcsc_scan &
sudo alpha -nograb -style motif &> $KCBLOGS
