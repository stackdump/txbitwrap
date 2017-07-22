#!/usr/bin/env python
import random
from twisted.internet import reactor
from txbitwrap.event import processor

class TicTacToe(processor.Factory):
    """ play tic-tac-toe w/ random strategy """

    name = 'octoe'

    board = ['00', '01', '02',
             '10', '11', '12',
             '20', '21', '22']

    def on_load(self):
        """ configure the handler """
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
                    print self.dispatch(
                        oid=event['oid'],
                        action=self.player + coords,
                        payload=event['payload'])
                    return

        reactor.callLater(0.5, move)
        random.shuffle(self.board)
