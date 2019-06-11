#!/usr/bin/env bash
sudo /etc/init.d/ntp stop
sudo ntpd -s
sudo /etc/init.d/ntp start
