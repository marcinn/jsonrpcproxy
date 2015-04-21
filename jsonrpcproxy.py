"""
Damn simple JSON-RPC client
"""

__author__ = "Marcin Nowak"
__copyright__ = "Copyright 2013"
__license__ = "BSD"
__maintainer__ = "Marcin Nowak"
__email__ = "marcin.j.nowak@gmail.com"


import requests
import uuid
import json
import logging
from requests.exceptions import RequestException as ConnectionError
from requests.exceptions import Timeout as TimeoutError


__all__ = ['ServiceProxy', 'JsonRpcError', 'HttpError', 'ConnectionError', 
    'TimeoutError', 'Client']

log = logging.getLogger(__name__)


class Client(object):
    def __init__(self, endpoint, timeout=10):
        self.endpoint = endpoint
        self.timeout = timeout

    def __getattr__(self, name):
        return Method(self, name)

    def call(self, method, params=None):
        request = {
                'method': str(method),
                'id': uuid.uuid4().hex,
                'jsonrpc': '2.0',
                }

        if params:
            request['params'] = params

        log.debug('Calling %s.%s() with params: %%s' % (self.endpoint, method), params)

        resp = requests.post(self.endpoint, data=json.dumps(request), timeout=self.timeout)
        resp_data = resp.text

        if not resp.status_code == 200:
            raise HttpError(message=resp_data, code=resp.status_code)

        log.debug('Response data: %s', resp_data)

        try:
            data = json.loads(resp_data)
        except ValueError, e:
            raise ExpectingJSONResponse(message=unicode(e), data=resp_data)

        ver = data.get('jsonrpc') or ''
        if not ver == '2.0':
            raise UnsupportedJsonRpcVersion(ver)

        if not request['id'] == data.get('id'):
            raise IdentifierMismatch

        if 'error' in data:
            error = data['error']
            raise exc_factory(error['code'], error.get('message'),
                    error.get('data'))

        return data['result']


class Method(object):
    def __init__(self, client, name):
        self.name = name
        self.client = client

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise ValueError('Use args or kwargs separately')
        return self.client.call(self, args or kwargs)

    def __str__(self):
        return self.name


class JsonRpcError(Exception):
    def __init__(self, message=None, code=None, data=None):
        self.args = filter(None, [message,code,data])
        self.message = message
        self.code = code
        self.data = data


class ParseError(JsonRpcError):
    pass


class InvalidRequest(JsonRpcError):
    pass


class MethodNotFound(JsonRpcError):
    pass


class InvalidParams(JsonRpcError):
    pass


class InternalError(JsonRpcError):
    pass


class ServerError(JsonRpcError):
    pass


class UnknownServerError(JsonRpcError):
    pass


class UnsupportedJsonRpcVersion(JsonRpcError):
    pass


class IdentifierMismatch(JsonRpcError):
    pass


class ExpectingJSONResponse(JsonRpcError):
    pass


class HttpError(Exception):
    def __init__(self, message=None, code=None):
        self.message = message
        self.code = code
        self.args = (code, message)



exc_map = {
        -32700: ParseError,
        -32600: InvalidRequest,
        -32601: MethodNotFound,
        -32602: InvalidParams,
        -32603: InternalError,
        }


def exc_factory(code, msg=None, data=None):
    cls = exc_map.get(code)
    if not cls:
        if code >= -32099 and code <= -32000:
            cls = ServerError
        else:
            cls = UnknownServerError
    return cls(msg,data=data)



ServiceProxy = Client # compat for v0.1


