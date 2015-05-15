
# Damn simple JSON-RPC client for Python

![](https://travis-ci.org/marcinn/jsonrpcproxy.svg?branch=master)
![](https://pypip.in/download/jsonrpcproxy/badge.svg)
![](https://pypip.in/version/jsonrpcproxy/badge.svg)
![](https://pypip.in/py_versions/jsonrpcproxy/badge.svg)
![](https://pypip.in/status/jsonrpcproxy/badge.svg)
![](https://pypip.in/license/jsonrpcproxy/badge.svg)

## What is JSON-RPC

JSON-RPC is a protocor similar to XML-RPC, but simpler and very lightweight.
There is no necessary to generate nor parse XML documents by using heavy librariers, and there are no dependencies.

For more information please read JSON-RPC v2.0 specification: http://www.jsonrpc.org/specification

## JSON-RPC implementations for Python

There are many implementations of JSON-RPC protocol in Python, mostly servers and clients in one package: http://en.wikipedia.org/wiki/JSON-RPC#Implementations

## Why another JSON-package?

Some time ago I was searching small, reliable and simple client (just client!) for calling JSON-RPC services,
without many (any) dependencies and without strange layers of wrappers, but with responses simplest as possible. 

Finally I've found nothing like that, so I wrote my own.

## Example

```python
import jsonrpcproxy as rpc

calculator = rpc.ServiceProxy('http://example.math.server/')

try:
  result = calculator.addNumbers(2,2)
except rpc.HttpError, e:
  print "HTTP error: %s (%s)" % (e, e.code)
except rpc.JsonRpcError, e:
  print "RPC Error: %s (%s)" % (e, e.code)
  print "RPC Error data: %s" % e.data
else:
  print "2 + 2 = %s" % result
  
```

## Goals for the stable release 

  * automatic tests
  * handling connection errors
  * documentation
  * 100% implementation of the JSON-RPC v2.0 specification (batches)

## Future

  * Python 3 support
  * further simplifications ;)
  
## Issues

Please use Github to report issues: https://github.com/marcinn/jsonrpcproxy/issues
