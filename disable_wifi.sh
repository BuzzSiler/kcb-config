#! /bin/bash
echo "@reboot sudo ifdown wlan0" | sudo tee --append /etc/cron.d/wifi_disable > /dev/null

