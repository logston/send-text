#!/bin/bash

TIME=$[( $RANDOM % 10 ) * 10]
echo "Sleeping for $TIME"
sleep ${TIME}m

cd /home/paul/send-text
source env.sh
python3 run.py
