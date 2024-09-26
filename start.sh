#!/usr/bin/bash

set -x

kill -9 $(lsof -i :10001)

python3 run.py >log.log 2>&1 &
