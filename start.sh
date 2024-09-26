#!/usr/bin/bash

set -x

nohup python3 run.py >log.log 2>&1 &
