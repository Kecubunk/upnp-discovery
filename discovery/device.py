import sys
import re
import uuid

from . import utils, constants
from .Base import ReactorManager


from twisted.internet import reactor, task
from twisted.internet.protocol import DatagramProtocol

import logging
logger = logging.getLogger(__name__)


class SearchServer(DatagramProtocol):

    def __init__(self, device):
        self.device = device

    def datagramReceived(self, datagram, address):
        message = utils.parseMessage(datagram)

        if(constants.searchRe.match(message['method'])):
            search = message.get('ST', None)
            if search in ('ssdp:all', self.device.type):
                logger.debug("search received: ")
                self.send_response(address)

    def send_response(self, address):
        logger.debug("Sending response")
        msg = self.device.getResponseMessage()
        self.transport.write(utils.build_message(msg), address)
"""
    Discoverable Device
"""


class Device(ReactorManager):

    def __init__(self, iface, id=None, type=None, name='device', version='1', delay=10):
        super(Device, self).__init__()

        self.uuid = uuid.uuid1() if id is None else id
        self.type = constants.DEVICE_TYPE if type is None else type
        self.name = name
        self.version = version
        self.delay = 3 if delay < 3 else delay
        self.iface = iface

    def getNotifyMessage(self):
        headers = [
            'NOTIFY * HTTP/1.1',
            'HOST: %s:%d' % (constants.SSDP_ADDR, constants.SSDP_PORT),
            'CACHE-CONTROL: max-age=%d' % self.delay,
            'LOCATION: http://notimplemented.com',
            'NT: %s' % (self.type),
            'NTS: ssdp:alive',
            'SERVER: OS X/10.11.6 UPnP/2.0 oneIDDevice/1',
            'USN:uuid:%s%s' % (self.uuid, self.type)
        ]
        return headers

    def getResponseMessage(self):
        usn = 'uuid:%susn:%s' % (self.uuid, self.type)
        headers = [
            'HTTP/1.1 200 OK',
            'HOST: %s:%d' % (constants.SSDP_ADDR, constants.SSDP_PORT),
            'CACHE-CONTROL: max-age=%d' % self.delay,
            'LOCATION: http://notimplemented.com',
            'NT: %s' % (self.type),
            'NTS: ssdp:alive',
            'SERVER: OS X/10.11.6 UPnP/2.0 oneIDDevice/1',
            'USN: uuid:%s%s' % (self.uuid, self.type),
            'ST: %s' % (self.type)
        ]
        return headers

    def send_notify(self):
        logger.debug("Sending NOTIFY...") 
        # msg = NO % (SSDP_ADDR, SSDP_PORT)
        msg = self.getNotifyMessage()
        port = reactor.listenUDP(0, DatagramProtocol(), interface=self.iface)
        port.write(utils.build_message(msg), (constants.SSDP_ADDR, constants.SSDP_PORT))
        port.stopListening()

    def start_discovery_server(self):
        # Begin listening for search requests
        self.multicastPort = reactor.listenMulticast(
            constants.SSDP_PORT, SearchServer(self), listenMultiple=True)
        self.multicastPort.setLoopbackMode(0)
        self.multicastPort.joinGroup(constants.SSDP_ADDR, interface=self.iface)

        # Begin announcing presence
        self.loopingCall = task.LoopingCall(self.send_notify)
        self.loopingCall.start(self.delay)

    def start(self):
        reactor.callWhenRunning(self.start_discovery_server)
        reactor.addSystemEventTrigger('before', 'shutdown', self.stop)
        self.reactor_runner()
