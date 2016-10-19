from twisted.internet import reactor


class ReactorManager:

    def __init__(self):
        reactor.addSystemEventTrigger('before', 'shutdown', self.stop)

    def when_ready(self, fn):
        reactor.callWhenRunning(fn)
        pass

    def before_shutdown(self, fn):
        reactor.addSystemEventTrigger('before', 'shutdown', fn)
        pass

    def start(self):
        reactor.run()
