#!/usr/bin/env bash

# Stop and Disable systemd ntp service
sudo systemctl stop ntp
sudo systemctl disable ntp

# Remove NTP package
sudo apt-get -y remove ntp

# Remove NTP components
sudo rm -f /etc/init.d/ntp
sudo rm -f /etc/default/ntp
sudo rm -f /etc/rc?.d/{S,K}??ntp
sudo rm -f /etc/ntp.conf
sudo rm -f /etc/cron.daily/ntp
sudo rm -f /var/log/ntpstats

# Modify /etc/systemd/timesyncd.conf to contain the following:
#[Time]
#Servers=0.north-america.pool.ntp.org 1.north-america.pool.ntp.org 2.north-america.pool.ntp.org 3.north-america.pool.ntp.org

# Edit /etc/rc.local and add the following before 'exit 0':
#[ ! -e /var/lib/systemd/clock -a "`systemctl is-active systemd-timesyncd | grep -i active`" ] && timedatectl set-ntp 1 > /dev/null 2>&1
#sleep 2

# Enable and start timesyncd service
#sudo systemctl enable systemd-timesyncd
#sudo systemctl start systemd-timesyncd
# Enable ntp
#sudo timedatectl set-ntp 1
