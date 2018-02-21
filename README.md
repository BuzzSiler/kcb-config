The KCB Config directory contains scripts and configuration files needed
to setup the KeyCodeBox application environment.

# KCB Scripts

## Starting KCB
KCB is started from .bashrc and looks for the file, kcb.conf in the /home/pi directory.
If kcb.conf is not found, the KeyCodeBox application will not start.  The kcb.conf file
contains definitions for environment variables: KCBCONFIG_ROOT and KCBCONFIG.  After
KCBCONFIG is defined, it is sourced.  If kcb.conf is found it is sourced and the kcb 
start script is invoked.

## KCB Start Script

## KCB Launch Script

## KCB Link Script

## KCB Pull and Build Script

## KCB Remote Desktop Script

# KCB Configuration

## KCB Config

# KCB Binaries

# KCB Images

# KCB Database

# KCB Logs

#KeyCodeBox Alpha
raspberry-pi touchscreen lockbox appliance

## Dependencies
- >= QT5.3.2
- libxml2
- fprint https://www.freedesktop.org/wiki/Software/fprint/libfprint/
- g++

## Building
```
$ git clone https://github.com/petrichorsystems/keycodebox.git
$ cd keycodebox/alpha
$ qmake && make
```

## Notes
Image directory currently set to:
```
/home/pi/dev/keycodebox/alpha/images
