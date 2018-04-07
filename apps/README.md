## Bitwrap Demo Applications

This directory contains bitwrap applications using Twisted's [.tac file format](http://twistedmatrix.com/documents/current/core/howto/application.html#twistd-and-tac)

The included ./Procfile is used to start each application using [honcho](https://github.com/nickstenning/honcho)


#### Api

Run only the bitwrap api server or leave our all args to run all apps

    honcho start api
