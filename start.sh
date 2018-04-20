#!/usr/bin/env bash

if [[ -f ./env.rc ]] ; then
    source env.rc
fi

twistd $TWISTD_OPTS bitwrap --listen-ip=0.0.0.0 --listen-port=8080

if [[ $? -eq 0 && -f twistd.pid ]] ; then
    PID=`cat twistd.pid`
    echo "started $PID"
    exit 0
else
    exit 1
fi;
