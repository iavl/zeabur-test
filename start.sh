#!/usr/bin/bash

set -x

process_id=$(lsof -i :10001)
kill -9 ${process_id}

nohup python3 run.py >log.log 2>&1 &
