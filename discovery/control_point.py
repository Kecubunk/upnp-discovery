import re
import uuid
import logging
logger = logging.getLogger(__name__)

from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

from . import utils, constants
from .Base import ReactorManager


"""
    Handles process when a device multicasts a message about its existence
"""


class DeviceNotifyServer(DatagramProtocol):

    def __init__(self, notify_callback=None, filter_function=None):
        default_filter = lambda x: True
        self.notify_callback = notify_callback
        self.filter_function = default_filter if filter_function is None else filter_function

    def datagramReceived(self, datagram, address):
        message = utils.parseMessage(datagram)
        if(constants.notifyRe.match(message['method'])):
            if(self.filter_function(message)):
                logger.info("device announcement: ", datagram, address)
                if(self.notify_callback is not None):
                    self.notify_callback(message, address)

"""
    Handles responses from devices after an M-SEARCH multicast
"""


class DeviceSearchResponse(DatagramProtocol):

    def __init__(self, callback=None):
        self.callback = callback
        pass

    def datagramReceived(self, datagram, address):
        message = utils.parseMessage(datagram)
        if(constants.responseRe.match(message['method'])):
            logger.info("device RESPONSE: ", datagram, address)
            if(self.callback is not None):
                self.callback(message, address)


class ControlPoint(ReactorManager):

    def __init__(self, iface):
        super(ControlPoint, self).__init__()
        self.iface = iface
        self.notify_callback = None

    # Client helpers
    def send_msearch(self, search, callback):
        port = reactor.listenUDP(0, DeviceSearchResponse(callback=callback), interface=self.iface)
        logger.info("Sending M-SEARCH...")
        msg = self.getSearchMessage(search=search)
        port.write(utils.build_message(msg), (constants.SSDP_ADDR, constants.SSDP_PORT))
        reactor.callLater(2.5, port.stopListening)  # MX + a wait margin

    def getSearchMessage(self, search='ssdp:all'):
        headers = [
            'M-SEARCH * HTTP/1.1',
            'HOST: %s:%d' % (constants.SSDP_ADDR, constants.SSDP_PORT),
            'MAN: "ssdp:discover"',
            'MX: %d' % (2),
            'ST: %s' % search
        ]
        return headers

    # Client API
    def start_searching(self, search=None, callback=None, interval=None):
        search_fn = lambda: self.send_msearch(search=search, callback=callback)

        if interval is not None:
            # Begin searching for devices
            self.loopingCall = task.LoopingCall(search_fn)
            self.loopingCall.start(interval)
        else:
            search_fn()

    def stop_searching(self):
        if self.loopingCall is not None:
            self.loopingCall.stop()

    # Server API
    def start_listening(self, filter_function=None):
        # Begin listening for notifications from devices
        self.multicastPort = reactor.listenMulticast(
            constants.SSDP_PORT, DeviceNotifyServer(notify_callback=self.notify_callback, filter_function=filter_function), listenMultiple=True)
        self.multicastPort.setLoopbackMode(1)
        self.multicastPort.joinGroup(constants.SSDP_ADDR, interface=self.iface)

    def on_notify(self, callback=None):
        self.notify_callback = callback

    def stop_listening(self):
        self.multicastPort.leaveGroup(constants.SSDP_ADDR, interface=self.iface)
        self.multicastPort.stopListening()

    def stop(self):
        self.stop_searching()
        self.stop_listening()
