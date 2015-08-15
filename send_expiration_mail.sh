#!/bin/bash

BASEDIR=$(dirname $0)
echo $BASEDIR

cd $BASEDIR

current_dir=$(pwd)
echo $current_dir

while true
do
        python pollExpiryCheck.py
        # sleep for 24 hours
        sleep 3600
done
