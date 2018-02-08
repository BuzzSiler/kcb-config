#!/bin/bash
find /home/pi/dev/keycodebox/alpha/ -type f -exec touch {} +
find /home/pi/dev/keycodebox/alpha.elms/ -type f -exec touch {} +
sudo find /usr/lib/arm-linux-gnueabihf/ -type f -exec touch {} +
