#!/usr/bin/env python
import random
from twisted.internet import reactor
from txbitwrap.event import processor

class TicTacToe(processor.Factory):
    """ play tic-tac-toe w/ random strategy """

    schema = 'octoe'

    board = ['00', '01', '02',
             '10', '11', '12',
             '20', '21', '22']

    WINSETS = [
        set(['00', '01', '02']),
        set(['10', '11', '12']),
        set(['20', '21', '22']),
        set(['00', '11', '22']),
        set(['02', '11', '20']),
        set(['00', '10', '20']),
        set(['01', '11', '21']),
        set(['02', '12', '22'])
    ]

    def on_load(self):
        """ configure the handler """
        self.move_key = 'turn_' + self.player.lower()

        self.config = {
            'exchange': 'bitwrap',
            'queue': 'player-' + self.player,
            'routing-key': self.schema
        }

    def find_winner(self, oid):
        """ search previous events for a win state """

        x_moves = []
        o_moves = []

        for frame in self.stream(self.schema, oid):

            coords = frame['action'][1:]

            if frame['action'][0] == 'X':
                x_moves.append(coords)
            elif frame['action'][0] == 'O':
                o_moves.append(coords)

        x_set = set(x_moves)
        o_set = set(o_moves)

        for winset in self.WINSETS:

            if winset.issubset(x_set):
                return 'X Wins'

            if winset.issubset(o_set):
                return 'O Wins'

        return None

    def on_event(self, opts, event):
        """ handle 'octoe' event from rabbit """
        statevector = self.state(self.schema, event['oid'])

        if statevector[self.move_key] == 0:
            return

        winner = self.find_winner(event['oid'])

        def end(msg):
            """ end the game declare the winner """
            print self.dispatch(
                oid=event['oid'],
                action='END_' + self.player,
                payload={'msg': msg}
            )

        def move():
            """ use first valid move """
            for coords in self.board:
                if statevector['m' + coords] > 0:
                    print self.dispatch(
                        oid=event['oid'],
                        action=self.player + coords,
                        payload=event['payload'])
                    return
            end('draw')

        if winner is None:
            reactor.callLater(0.5, move)
            random.shuffle(self.board)
        else:
            end(winner)
