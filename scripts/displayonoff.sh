
#!/usr/bin/env bash

if test -f "/sys/class/backlight/rpi_backlight/bl_power"; then
    echo $1 > /sys/class/backlight/rpi_backlight/bl_power
fi
