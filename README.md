# upnp-discovery
Simple device discovery python library

This library is a thin wrapper around the twisted library that implements some of the conventions of UPnP/2.0

There are 2 classes organized around the UPnP role being implemented:
- ControlPoint
- Device

ControlPoint
------------

A control point is a node that may want to interact with (or atleast discover) the available services on a network.


Basic Usage
```
from discovery import ControlPoint

# The interface the service should attach to
iface = '0.0.0.0'

# The port on which the searching socket will open and listen for responses
port = 7777

cp = ControlPoint(iface, listener_port=port)

# The type of device to search for
device_type = 'urn:oneid.neustar.biz:device:Programmer:1.0'

# A callback whenever a device is found
def device_responded(message, address):
    print('DEVICE FOUND')
    print(json.dumps(message, indent=4, sort_keys=True))

# A bootstrap function to be called when the service is running
def ready():
    # Set a filter to only return devices that match the set type
    obj.start_listening(
        filter_function=lambda m: m.get('NT') == device_type)
    # Begin sending search messages every 10 seconds
    obj.start_searching(search=device_type, callback=device_responded, interval=10)

# Attach the bootstrap function
obj.when_ready(ready)

# Initialized the service
obj.start()
```


Device
------

A device is a node in a network that exposes some service to the rest of the network


Basic Usage:
```
from discovery import Device

discoverable_server = Device(iface, type='urn:oneid.neustar.biz:device:Programmer:1.0')
discoverable_server.start()
```

Custom Header:
```
from discovery import Device

class CustomDevice(Device):

    def __init__(self, *args, **kwargs):
        # Remove our custom kwarg
        self.port = kwargs.pop('port', None)
        super(ProgDevice, self).__init__(*args, **kwargs)

    def create_port_header(self):
        return "provisioning_port.oneid.neustar.biz: %s" % self.port

    # Override the notify message builder to include our new header
    def getNotifyMessage(self):
        headers = super(ProgDevice, self).getNotifyMessage()
        headers.append(self.create_port_header())
        return headers
    
    # Override the search response message builder to include our new header
    def getResponseMessage(self):
        headers = super(ProgDevice, self).getResponseMessage()
        headers.append(self.create_port_header())
        return headers

# Interface to bind to
iface = '0.0.0.0'

# What type of device to notify as and respond to searches for
device_type = 'urn:oneid.neustar.biz:device:Programmer:1.0'

# Custom header data
port = 9999

discoverable_server = CustomDevice('0.0.0.0', type=device_type, port=port)
discoverable_server.start()
```
