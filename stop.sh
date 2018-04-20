#!/usr/bin/env bash

if [[ -f twistd.pid ]] ; then
    PID=`cat twistd.pid`
    kill $PID
    if [[ $? -eq 0 ]] ; then
      echo "stopped $PID"
      exit 0
    fi
else
    echo 'missing twistd.pid'
    exit 1
fi
