#!/usr/bin/env python
import random
from twisted.internet import defer, reactor
from twisted.python import log
from txbitwrap.event import processor

class TicTacToe(processor.Factory):
    """ play tic-tac-toe w/ random strategy """

    schema = 'octoe'

    board = ['00', '01', '02',
             '10', '11', '12',
             '20', '21', '22']

    winning_sets = (set(('00', '01', '02')),
                    set(('10', '11', '12')),
                    set(('20', '21', '22')),
                    set(('00', '11', '22')),
                    set(('02', '11', '20')),
                    set(('00', '10', '20')),
                    set(('01', '11', '21')),
                    set(('02', '12', '22')))

    def on_load(self):
        """ configure the handler """

        self.move_key = 'turn_' + self.player.lower()

        self.config = {
            'exchange': 'bitwrap',
            'queue': 'player-' + self.player,
            'routing-key': self.schema
        }

    @defer.inlineCallbacks
    def on_event(self, opts, event):
        """ handle 'octoe' event from rabbit """
        state = yield self.state(self.schema, event['oid'])
        statevector = state['state']

        if statevector[self.move_key] != 0:

            winner = yield self.find_winner(event['oid'])

            def end(msg):
                """ end the game with message about winning player """
                d = self.dispatch(
                    oid=event['oid'],
                    action='END_' + self.player,
                    payload={'msg': msg}
                )

                d.addCallback(lambda event: log.msg(event))
                return d

            def move():
                """ select first valid move and emit an event """
                for coords in self.board:
                    if statevector['m' + coords] > 0:
                        d = self.dispatch(
                            oid=event['oid'],
                            action=self.player + coords,
                            payload=event['payload'])

                        d.addCallback(lambda evt: log.msg(evt))
                        return d
                return end('Draw')

            if winner is None:
                reactor.callLater(0.5, move)
                random.shuffle(self.board)
            else:
                end(winner)

    @defer.inlineCallbacks
    def find_winner(self, oid):
        """ search event stream for a win state """
        x_moves = []
        o_moves = []

        stream = yield self.stream(self.schema, oid)

        winner = None

        if len(stream) > 5:

            for event in stream:

                coords = event['action'][1:]

                if event['action'][0] == 'X':
                    x_moves.append(coords)
                elif event['action'][0] == 'O':
                    o_moves.append(coords)

            for winset in self.winning_sets:

                if winset.issubset(x_moves):
                    winner = 'X Wins'
                elif winset.issubset(o_moves):
                    winner = 'O Wins'

        defer.returnValue(winner)
