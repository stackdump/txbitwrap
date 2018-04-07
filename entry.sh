#!/usr/bin/env bash

if [[ -f ./env.rc ]] ; then
    source env.rc
fi

export PYTHONPATH=./

if [[ "x${PNML_PATH}" = 'x' ]] ; then
    export PNML_PATH=./schemata
fi

honcho start $@
