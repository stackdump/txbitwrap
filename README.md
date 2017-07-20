# txbitwrap

[![Build Status](https://travis-ci.org/stackdump/txbitwrap.svg?branch=master)](https://travis-ci.org/stackdump/txbitwrap)

An event-oriented service using a PostgreSQL database as an eventstore.
Fork of http://getbitwrap.com

This library is build to run atop an event-driven networking engine called: [Twisted](https://twistedmatrix.com/trac/)

#### Status

Modifying bitwrap eventstore to provide a reactor-driven event toolkit.

Here's an example of a handler for playing tic-tac-toe using an eventstream.


    #!/usr/bin/env python
    import random
    from twisted.internet import reactor
    from txbitwrap.event.processor import Factory

    class TicTacToe(Factory):
        """
        play tic-tac-toe
        w/ random strategy
        """

        name = 'octoe'

        board = ['00', '01', '02',
                 '10', '11', '12',
                 '20', '21', '22']

        config = None

        def on_load(self):
            self.move_key = 'turn_' + self.player.lower()

            self.config = {
                'exchange': 'bitwrap',
                'queue': 'player-' + self.player,
                'routing-key': self.name
            }

        def on_event(self, opts, event):
            """ handle 'octoe' event from rabbit """
            statevector = self.state(event['oid'])

            if statevector[self.move_key] == 0:
                return

            def move():
                for coords in self.board:
                    if statevector['m' + coords] > 0:
                        print self.dispatch(event['oid'], self.player + coords, event['payload'])
                        return

            reactor.callLater(0.5, move)
            random.shuffle(self.board)

#### Docker

[![Docker](https://img.shields.io/docker/automated/stackdump/txbitwrap.svg)](https://hub.docker.com/r/stackdump/txbitwrap/~/dockerfile/)

Run development database & server

    docker run -d --name bitwrap-dev -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=bitwrap postgres:9.6

    # TODO: include instructions run this container and how to link w/ postgresql container above

    docker run -d --hostname rabbit-dev --name rabbit-dev -e RABBITMQ_DEFAULT_USER=bitwrap -e RABBITMQ_DEFAULT_PASS=bitwrap  -p 127.0.0.1:5672:5672 -p 127.0.0.1:15672:15672 rabbitmq:3-management
