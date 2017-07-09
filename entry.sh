#!/usr/bin/env bash
PYTHONPATH=./ twistd -n bitwrap --listen-ip=0.0.0.0 --listen-port=8080 
