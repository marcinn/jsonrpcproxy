"""
Damn simple JSON-RPC client
"""

__author__ = "Marcin Nowak"
__copyright__ = "Copyright 2013"
__license__ = "BSD"
__maintainer__ = "Marcin Nowak"
__email__ = "marcin.j.nowak@gmail.com"


import urllib
import uuid
import json
import logging

__all__ = ['ServiceProxy']

log = logging.getLogger(__name__)


class ServiceProxy(object):
    """
    Remote service proxy class.

    This is main class of the package.
    Class must be instantiated with URL of remote service (`endpoint`).

    :param endpoint: an URL of the RPC-JSON service
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __getattr__(self, name):
        """
        Instantiate and return a :class:Method with specified `name`

        :param name: name of remote method
        """

        return Method(self, name)

    def call(self, method, params=None):
        """
        Call remote `method` with optional `params`
        passed as a `dict`-like or `list`-like objects

        :param method: name of a remote method or a `Method` instance
        :param params: optional `dict`-like or `list`-like object
                       which will be passed as an argument of the method
        """

        request = {
                'method': str(method),
                'id': uuid.uuid4().hex,
                'jsonrpc': '2.0',
                }

        if params:
            request['params'] = params

        log.debug('Calling %s.%s() with params: %%s' % (self.endpoint, method), params)

        resp = urllib.urlopen(self.endpoint, json.dumps(request))
        resp_data = resp.read()

        if not resp.code == 200:
            raise HttpError(message=resp_data, code=resp.code)

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
    """
    Class for representation and calling a remote method
    """

    def __init__(self, client, name):
        self.name = name
        self.client = client

    def __call__(self, *args, **kwargs):
        """
        Shorthand for the `ServiceProxy.call()`

        :param *args: positional arguments of the remote method
        :param **kwargs: arguments passed as a dict to the remote method

        Only `*args` or `**kwargs` should be specified
        and cannot be mixed together.
        """

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



