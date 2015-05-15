from nose.tools import *
import jsonrpcproxy as rpc


def test_method_name_chaining():
    client= rpc.Client('')
    assert client.method1.method2._name == 'method1.method2'


def test_client_propagation_on_method_chaining():
    client = rpc.Client('')
    assert client.method1.method2._client is client


def test_method_string_representation():
    client = rpc.Client('')
    assert str(client.method1) == 'method1'


def test_chained_method_string_representation():
    client = rpc.Client('')
    assert str(client.method1.method2) == 'method1.method2'


@raises(ValueError)
def test_that_method_cant_be_called_with_mixed_type_args():
    client = rpc.Client('')
    client.method1('a', b=2)


def test_hiding_url_password_func():
    mangled_url= rpc.hide_url_password('http://user:password@example.com')
    assert mangled_url == 'http://user:*****@example.com'



