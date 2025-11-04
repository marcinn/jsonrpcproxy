"""
Damn simple JSON-RPC client

This module provides a client for interacting with JSON-RPC 2.0 services.
It handles request serialization, response deserialization, and error handling.
"""

from __future__ import print_function

__author__ = "Marcin Nowak"
__copyright__ = "Copyright 2013"
__license__ = "BSD"
__maintainer__ = "Marcin Nowak"
__email__ = "marcin.j.nowak@gmail.com"


import json
import logging
import re
import uuid

import requests

__all__ = [
    "ServiceProxy",
    "JsonRpcError",
    "HttpError",
    "Client",
    "ParseError",
    "InvalidRequest",
    "MethodNotFound",
    "InvalidParams",
    "InternalError",
    "ServerError",
    "UnknownServerError",
    "UnsupportedJsonRpcVersion",
    "IdentifierMismatch",
    "ExpectingJSONResponse",
]

log = logging.getLogger(__name__)


RE_PASSWD = re.compile(r"//(.+):.+@")


def hide_url_password(url):
    """
    Hides the password in a given URL for display purposes.

    Args:
        url (str): The URL string.

    Returns:
        str: The URL with the password replaced by '*****'.
    """
    return RE_PASSWD.sub("//\\1:*****@", url)


class Client:
    """
    A JSON-RPC client for making remote procedure calls.

    Args:
        endpoint (str): The URL of the JSON-RPC server.
        timeout (int, optional): The timeout for requests in seconds. Defaults to 10.
        strict (bool, optional): If True, enforces JSON-RPC 2.0 strictness. Defaults to True.
    """

    def __init__(self, endpoint, timeout=10, strict=True):
        """
        Initializes the JSON-RPC client.

        Args:
            endpoint (str): The URL of the JSON-RPC server.
            timeout (int): The timeout for requests in seconds.
            strict (bool): If True, enforces JSON-RPC 2.0 strictness.
        """
        self._endpoint = endpoint
        self._printable_endpoint = hide_url_password(self._endpoint)
        self._strict = strict
        self._timeout = timeout

    def __getattr__(self, name):
        """
        Allows calling remote methods as attributes of the client object.

        Args:
            name (str): The name of the remote method.

        Returns:
            Method: A Method object representing the remote method.
        """
        return Method(self, name)

    def _call(self, method, params=None):
        """
        Makes a JSON-RPC call to the configured endpoint.

        Args:
            method (str): The name of the remote method to call.
            params (dict or list, optional): The parameters for the remote method. Defaults to None.

        Returns:
            any: The result of the remote method call.

        Raises:
            HttpError: If the HTTP request fails.
            ExpectingJSONResponse: If the response is not valid JSON.
            UnsupportedJsonRpcVersion: If the JSON-RPC version is not 2.0 and strict mode is enabled.
            IdentifierMismatch: If the response ID does not match the request ID.
            JsonRpcError: If the remote method returns an error.
        """
        request = {
            "method": str(method),
            "id": uuid.uuid4().hex,
            "jsonrpc": "2.0",
        }

        if params:
            request["params"] = params

        log.debug(
            "Calling %s `%s` with params: %s", self._printable_endpoint, method, params
        )

        resp = requests.post(
            self._endpoint,
            data=json.dumps(request),
            timeout=self._timeout,
            headers={"content-type": "application/json"},
        )
        resp_data = resp.text

        if not resp.status_code == 200:
            raise HttpError(message=resp_data, code=resp.status_code)

        log.debug("Response data: %s", resp_data)

        try:
            data = json.loads(resp_data)
        except ValueError as e:
            raise ExpectingJSONResponse(message=str(e), data=resp_data) from e

        ver = data.get("jsonrpc") or ""
        if self._strict and not ver == "2.0":
            raise UnsupportedJsonRpcVersion(ver)

        if not request["id"] == data.get("id"):
            raise IdentifierMismatch

        if "error" in data and data["error"]:
            error = data["error"]
            raise exc_factory(error["code"], error.get("message"), error.get("data"))

        return data["result"]


class Method:
    """
    Represents a remote method that can be called via the JSON-RPC client.

    Args:
        client (Client): The JSON-RPC client instance.
        name (str): The name of the remote method.
    """

    def __init__(self, client, name):
        """
        Initializes a Method object.

        Args:
            client (Client): The JSON-RPC client instance.
            name (str): The name of the remote method.
        """
        self._name = name
        self._client = client

    def __call__(self, *args, **kwargs):
        """
        Calls the remote method with the given arguments.

        Args:
            *args: Positional arguments for the remote method.
            **kwargs: Keyword arguments for the remote method.

        Returns:
            any: The result of the remote method call.

        Raises:
            ValueError: If both positional and keyword arguments are used simultaneously.
        """
        if args and kwargs:
            raise ValueError("Use args or kwargs separately")
        return self._client._call(self, args or kwargs)

    def __getattr__(self, name):
        """
        Allows chaining method calls for nested remote methods.

        Args:
            name (str): The name of the nested method.

        Returns:
            Method: A new Method object representing the nested remote method.
        """
        return Method(self._client, f"{self._name}.{name}")

    def __str__(self):
        """
        Returns the full name of the remote method.

        Returns:
            str: The name of the remote method.
        """
        return self._name


class JsonRpcError(Exception):
    """
    Base exception for JSON-RPC errors.

    Attributes:
        message (str): The error message.
        code (int): The error code.
        data (any): Additional error data.
    """

    def __init__(self, message=None, code=None, data=None):
        """
        Initializes a JsonRpcError.

        Args:
            message (str, optional): The error message. Defaults to None.
            code (int, optional): The error code. Defaults to None.
            data (any, optional): Additional error data. Defaults to None.
        """
        self.args = [arg for arg in (message, code, data) if arg is not None]
        self.message = message
        self.code = code
        self.data = data


class ParseError(JsonRpcError):
    """
    Represents a Parse Error (-32700).
    """


class InvalidRequest(JsonRpcError):
    """
    Represents an Invalid Request Error (-32600).
    """


class MethodNotFound(JsonRpcError):
    """
    Represents a Method Not Found Error (-32601).
    """


class InvalidParams(JsonRpcError):
    """
    Represents an Invalid Params Error (-32602).
    """


class InternalError(JsonRpcError):
    """
    Represents an Internal Error (-32603).
    """


class ServerError(JsonRpcError):
    """
    Represents a Server Error (-32099 to -32000).
    """


class UnknownServerError(JsonRpcError):
    """
    Represents an Unknown Server Error.
    """


class UnsupportedJsonRpcVersion(JsonRpcError):
    """
    Represents an Unsupported JSON-RPC Version Error.
    """


class IdentifierMismatch(JsonRpcError):
    """
    Represents an Identifier Mismatch Error.
    """


class ExpectingJSONResponse(JsonRpcError):
    """
    Represents an error when an expected JSON response is not received.
    """


class HttpError(Exception):
    """
    Represents an HTTP error during the JSON-RPC communication.

    Attributes:
        message (str): The HTTP error message.
        code (int): The HTTP status code.
    """

    def __init__(self, message=None, code=None):
        """
        Initializes an HttpError.

        Args:
            message (str, optional): The HTTP error message. Defaults to None.
            code (int, optional): The HTTP status code. Defaults to None.
        """
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
    """
    Factory function to create appropriate JSON-RPC exception instances based on the error code.

    Args:
        code (int): The error code.
        msg (str, optional): The error message. Defaults to None.
        data (any, optional): Additional error data. Defaults to None.

    Returns:
        JsonRpcError: An instance of a specific JsonRpcError subclass.
    """
    cls = exc_map.get(code)
    if not cls:
        if -32099 <= code <= -32000:
            cls = ServerError
        else:
            cls = UnknownServerError
    return cls(msg, data=data)


ServiceProxy = Client  # compat for v0.1
