""" watch for modifications to ./docs folder """

from twisted.internet import inotify
from twisted.internet import task
from twisted.python import filepath
from twisted.python import log
from twisted.application.service import IService
from zope.interface import implements
from txbitwrap.event import HANDLERS

class SessionWatch(object):
    """ observer websocket subscribers """
    implements(IService)

    interval = 60 * 60 * 24 # 1 day
    """ looping call interval in seconds """

    def __init__(self):
        self.name = __name__
        self.loop = task.LoopingCall(self.session_sweep)

    def privilegedStartService(self):
        """ required by IService """

    def startService(self):
        """ start service """
        log.msg('__SERVICE__ => ' + self.name)
        self.loop.start(self.interval)

    def stopService(self):
        """ stop service """
        log.msg('stopping %s' % self.name)

    def session_sweep(self):
        """ sweep websocket sessions """
        # FIXME: integrate w/ Auth + Sessions
        # websocket handlers should expire
        HANDLERS = {} # KLUDGE just purge all subscribers/handlers
