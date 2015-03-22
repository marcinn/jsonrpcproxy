Getting started
===============

Introduction
------------

Usage of :mod:`jsonrpcproxy` is very simple and intuitive.

After creation of :class:`ServiceProxy` instance you can call
any remote method like a regular Python`s method that belongs to
object.

Let's assume that some kind of remote calculator provides three methods:
`add`, `sub` and `div`, which takes exactly two arguments::

    >>> import jsonrpcproxy as rpc
    >>> calc = rpc.ServiceProxy('https://calculator.example.com/jsonrpc')
    >>> calc.add(2,4)
    6
    >>> calc.sub(8,2)
    6
    >>> calc.div(18,3)
    6


Return value of called method contains value returned by remote method.
This is not an instance of some kind of a response meta object.

But what about errors? They are passed as a exceptions of the
:class:`HttpError`, or type inherited from :class:`JsonRpcError` when
remote method is returning an error. Exception objects contains all
required data.

That's why :mod:`jsonrpcproxy` is so simple and intuitive.


Passing arguments to a method
-----------------------------


Exceptions handling
-------------------


