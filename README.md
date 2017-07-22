# txbitwrap

[![Build Status](https://travis-ci.org/stackdump/txbitwrap.svg?branch=master)](https://travis-ci.org/stackdump/txbitwrap)

An event-oriented service using a PostgreSQL database as an eventstore.
Fork of http://getbitwrap.com

This library is build to run atop an event-driven networking engine called: [Twisted](https://twistedmatrix.com/trac/)

### Status

Modifying bitwrap eventstore to provide a reactor-driven event toolkit.

#### Demo - Tic-Tac-Toe

* Try sending game events yourself
  * using manual events trigger by clicking the board in-browser

````
    ./entry.sh api
````


OR 

* use the apps/player-X.tac apps/player-O.tac files
  * to simulate a game using random play event processors

````
    ./entry.sh api X O
````

Then 

* visit http://127.0.0.1:8080#octothorpe
* click 'Rest' to create a new game
  * if using Procfile you will see the game progress
  * otherwise click on the gameboard to make moves


#### Docker

[![Docker](https://img.shields.io/docker/automated/stackdump/txbitwrap.svg)](https://hub.docker.com/r/stackdump/txbitwrap/~/dockerfile/)

Run development database & server

    docker run -d --name bitwrap-dev -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=bitwrap postgres:9.6

    # TODO: include instructions run this container and how to link w/ postgresql container above

    docker run -d --hostname rabbit-dev --name rabbit-dev -e RABBITMQ_DEFAULT_USER=bitwrap -e RABBITMQ_DEFAULT_PASS=bitwrap  -p 127.0.0.1:5672:5672 -p 127.0.0.1:15672:15672 rabbitmq:3-management
