#!/usr/bin/ bash

sudo systemctl stop apache2
sudo systemctl disable apache2
# dhcpcd is needed by SSH service
#sudo systemctl stop dhcpcd
#sudo systemctl disable dhcpcd
sudo systemctl stop bluetooth.service bluetooth.target
sudo systemctl disable bluetooth.service bluetooth.target
sudo systemctl stop samba.service
sudo systemctl disable samba.service
sudo systemctl stop cups cups-browsed cups.path cups.socket
sudo systemctl disable cups cups-browsed cups.path cups.socket
