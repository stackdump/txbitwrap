# txbitwrap

[![Build Status](https://travis-ci.org/stackdump/txbitwrap.svg?branch=master)](https://travis-ci.org/stackdump/txbitwrap)

An event-oriented service using a PostgreSQL database as an eventstore.
Fork of http://getbitwrap.com

#### Status

Integrating bitwrap eventstore with a reactor-driven application toolkit.

#### Docker

[![Docker](https://img.shields.io/docker/automated/stackdump/txbitwrap.svg)](https://hub.docker.com/r/stackdump/txbitwrap/~/dockerfile/)

Run development database & server

    docker run -d --name bitwrap-dev -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=bitwrap postgres:9.6

    # TODO: include instructions run this container and how to link w/ postgresql container above
