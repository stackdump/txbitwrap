#!/usr/bin/env bash
twistd -n bitwrap --listen-ip=0.0.0.0 --listen-port=8080 --pg-username=postgres --pg-password=bitwrap --pg-database=bitwrap
