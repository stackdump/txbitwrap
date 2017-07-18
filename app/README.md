## Bitwrap Demo Applications

This directory contains bitwrap applications using Twisted's [.tac file format](http://twistedmatrix.com/documents/current/core/howto/application.html#twistd-and-tac)

The included ./Procfile is used to start each application using [honcho](https://github.com/nickstenning/honcho)


#### Api

Run only the bitwrap api server

    honcho start api

#### Octoe

A bot that will play tic-tac-toe against you over RabbitMQ

    honcho start api octoe

