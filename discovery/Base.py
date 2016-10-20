from twisted.internet import reactor


class ReactorManager:

    def when_ready(self, fn):
        reactor.callWhenRunning(fn)

    def before_shutdown(self, fn):
        reactor.addSystemEventTrigger('before', 'shutdown', fn)

    def reactor_runner(self):
        reactor.run()

    def start(self):
        self.reactor_runner()

    def stop(self):
        reactor.stop()
