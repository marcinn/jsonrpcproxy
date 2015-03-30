Getting started
===============


Introduction
------------

Usage of :mod:`jsonrpcproxy` is very simple and intuitive client library
for calling remote JSON-RPC services based on v2.0 specification.

JSON-RPC is a protocol built over HTTP which uses simple JSON objects as a
transport layer. JSON-RPC is similar to XML-RPC but is lightweight,
simpler and easy for use. 

For more information about protocol please visit http://json-rpc.org/


Usage
-----

To call JSON-RPC service methods you must instantiate a proxy
:class:`ServiceProxy` first.  After that you can call any remote method like
a regular Python`s method that belongs to object.

Let's assume that some kind of remote calculator provides three methods:
`add`, `sub` and `div`, and every of them takes exactly two arguments::

    >>> import jsonrpcproxy as rpc
    >>> calc = rpc.ServiceProxy('https://calculator.example.com/jsonrpc')
    >>> calc.add(2,4)
    6
    >>> calc.sub(8,2)
    6
    >>> calc.div(18,3)
    6


Please note that return value of a method call contains value transfered
from remote service. This is not an instance of a response meta object,
but a pure result of the operation.

But what about errors? They are passed as a exceptions of the
:class:`HttpError`, or type inherited from :class:`JsonRpcError` if
remote method is returning an RPC error. Exceptions contains all
required data.

That's why :mod:`jsonrpcproxy` is so simple and intuitive.


Passing arguments to a method
-----------------------------


Exceptions handling
-------------------


