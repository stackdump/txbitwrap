#!/usr/bin/env python
from txbitwrap import Options, factory, bind
import txbitwrap

app_name = 'octoe'
options = Options.from_env({ 'external-queue': app_name, 'worker': 1 })
application = factory(app_name, options)

def bot(opts, event):
    """ respond to events from api """
    print '__bot__', event # FIXME actually play tic-tac-toe

bind(app_name, options, bot)
