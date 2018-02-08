#!/bin/bash
ps aux | grep alpha | cut -d' ' -f7 | sudo xargs kill -9
ps aux | grep alpha | cut -d' ' -f9 | sudo xargs kill -9
