'''
Copyright (c) <2012> Tarek Galal <tare2.galal@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os, base64

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class HttpProxy:
    def __init__(self, proxy=None, rtype='dict'):
        '''
        :type proxy: str
        :type rtype: Literal['dict', 'str']
        '''
        self._rtype = rtype
        self._parse(proxy)
        self.state = 'init'

    def _parse(self, proxy):
        '''
        :param proxy: String with HTTP(s) proxy in pythonic format as following:
        >>> # http[s]://{user}:{pwd}@{ip}:{port}
        >>> # or http[s]://{ip}:{port} 
        :type proxy: str
        :return:
        :rtype: Optional[Tuple[str, int, Optional[str]]]
        '''
        if isinstance(proxy, str):
            proxy = urlparse(proxy)
            if not all((proxy.hostname, proxy.port)):
                raise ValueError('Proxy has wrong format')
            self.host = proxy.hostname
            self.port = proxy.port
            self.auth = self._proxy_auth(proxy.username, proxy.password)
        else:
            self.host = self.port = self.auth = None
    
    def _proxy_auth(self, user, pwd):
        '''
        :type user: str
        :type pwd: str
        :return:
        :rtype: Optional[Union[Dict[str, str], str]]
        '''
        if all((user, pwd)):
            token = base64.b64encode(bytes(f"{user}:{pwd}", "utf-8")).decode("ascii")
            if self._rtype == 'dict':
                return {"Proxy-Authorization": f"Basic {token}"}
            else:
                return f"Proxy-Authorization: Basic {token}"