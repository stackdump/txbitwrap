#!/usr/bin/env bash

# use env var from docker --link if RDS_HOST env is not already set
if [[ "x${RDS_HOST}" = 'x'  && "x${RDS_PORT_5432_TCP_ADDR}" != "x" ]] ; then
    export RDS_HOST=$RDS_PORT_5432_TCP_ADDR # see: ./run.sh example using --link
fi

if [[ "x${PNML_PATH}" = 'x' ]] ; then
    export PNML_PATH=./schemata
fi

export PYTHONPATH=./
twistd -n bitwrap --listen-ip=0.0.0.0 --listen-port=8080 --redispatch=1
