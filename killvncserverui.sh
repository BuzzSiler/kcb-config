#!/usr/bin/env bash

arr=(`ps -auxc | grep 'vncserverui' | grep -v grep | awk '{print $2}'`)

for i in "${arr[@]}"; do kill -9 $i; done
