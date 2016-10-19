import re

SSDP_ADDR = '239.255.255.250'
SSDP_PORT = 1900
DEVICE_TYPE = 'urn:schemas-upnp-org:device:Basic:1.0'

searchRe = re.compile('^M-SEARCH')
notifyRe = re.compile('^NOTIFY')
responseRe = re.compile('^HTTP/1.1')
