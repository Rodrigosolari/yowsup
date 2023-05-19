import time

from yowsup.layers.network.dispatcher.dispatcher import YowConnectionDispatcher
from yowsup.common.http import HttpProxy

import asyncore
import logging
import socket
import traceback

logger = logging.getLogger(__name__)


class AsyncoreConnectionDispatcher(YowConnectionDispatcher, asyncore.dispatcher_with_send):
    def __init__(self, connectionCallbacks, proxy=None):
        super(AsyncoreConnectionDispatcher, self).__init__(connectionCallbacks)
        asyncore.dispatcher_with_send.__init__(self)
        self._connected = False
        self._proxy_connected = False
        self.proxy = HttpProxy(proxy, rtype='str')

    def sendData(self, data):
        if self._connected:
            self.out_buffer = self.out_buffer + data
            self.initiate_send()
        else:
            logger.warn("Attempted to send %d bytes while still not connected" % len(data))

    def connect(self, host):
        self.host = host
        logger.debug("connect(%s)" % str(host))
        self.connectionCallbacks.onConnecting()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        if self.proxy.host and self.proxy.port:
            asyncore.dispatcher_with_send.connect(self, (self.proxy.host, self.proxy.port))
        else:
            asyncore.dispatcher_with_send.connect(self, host)
        asyncore.loop(timeout=1)

    def send_proxy_connect_request(self):
        addr, port = self.host
        proxy_request = f"CONNECT {addr}:{port} HTTP/1.1\r\nHost: {addr}:{port}\r\n"
        if self.proxy.auth:
            proxy_request += self.proxy.auth
            proxy_request += "\r\n\r\n"
        self.send(proxy_request.encode(encoding='ascii'))
        self.socket.settimeout(10)
        data = b''
        while not data.endswith(b'\r\n\r\n'):
            data += self.recv(1)
        logger.debug("Received connection data from proxy: %s" % data.decode("utf-8").strip())

    def handle_connect(self):
        logger.debug("handle_connect")
        if not self._connected:
            self._connected = True
            if self.proxy.host and self.proxy.port:
                self.send_proxy_connect_request()
            self.connectionCallbacks.onConnected()

    def handle_close(self):
        logger.debug("handle_close")
        self.close()
        self._connected = False
        self.connectionCallbacks.onDisconnected()

    def handle_error(self):
        logger.error(traceback.format_exc())
        self.handle_close()

    def handle_read(self):
        data = self.recv(1024)
        self.connectionCallbacks.onRecvData(data)

    def disconnect(self):
        logger.debug("disconnect")
        self.handle_close()
