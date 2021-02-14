import json
import os

import pytest

from eip712_structs import EIP712Struct, String, make_domain, Bytes


def test_flat_struct_to_message():
    class Foo(EIP712Struct):
        s = String()

    domain = make_domain(name='domain')
    foo = Foo(s='foobar')

    expected_result = {
        'primaryType': 'Foo',
        'types': {
            'EIP712Domain': [{
                'name': 'name',
                'type': 'string',
            }],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'domain': {
            'name': 'domain',
        },
        'message': {
            's': 'foobar'
        }
    }

    message = foo.to_message(domain)
    assert message == expected_result

    # Now test in reverse...
    new_struct, domain = EIP712Struct.from_message(expected_result)
    assert new_struct.type_name == 'Foo'

    members_list = new_struct.get_members()
    assert len(members_list) == 1
    assert members_list[0][0] == 's'
    assert members_list[0][1].type_name == 'string'

    assert new_struct['s'] == 'foobar'


def test_nested_struct_to_message():
    class Bar(EIP712Struct):
        s = String()

    class Foo(EIP712Struct):
        s = String()
        bar = Bar

    domain = make_domain(name='domain')

    foo = Foo(
        s="foo",
        bar=Bar(s="bar")
    )

    expected_result = {
        'primaryType': 'Foo',
        'types': {
            'EIP712Domain': [{
                'name': 'name',
                'type': 'string',
            }],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }, {
                'name': 'bar',
                'type': 'Bar',
            }],
            'Bar': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'domain': {
            'name': 'domain',
        },
        'message': {
            's': 'foo',
            'bar': {
                's': 'bar',
            }
        }
    }

    message = foo.to_message(domain)
    assert message == expected_result

    # And test in reverse...
    new_struct, new_domain = EIP712Struct.from_message(expected_result)
    assert new_struct.type_name == 'Foo'

    members = new_struct.get_members()
    assert len(members) == 2
    assert members[0][0] == 's' and members[0][1].type_name == 'string'
    assert members[1][0] == 'bar' and members[1][1].type_name == 'Bar'

    bar_val = new_struct['bar']
    assert bar_val.type_name == 'Bar'
    assert bar_val['s'] == 'bar'

    assert foo.hash_struct() == new_struct.hash_struct()


def test_missing_field_from_message_error():
    message = {
        'primaryType': 'Foo',
        'types': {
            'EIP712Domain': [{
                'name': 'name',
                'type': 'string',
            }],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'domain': {
            'name': 'domain',
        },
        'message': {
        }
    }

    with pytest.raises(KeyError):
        EIP712Struct.from_message(message)


def test_null_field_from_message_error():
    message = {
        'primaryType': 'Foo',
        'types': {
            'EIP712Domain': [{
                'name': 'name',
                'type': 'string',
            }],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'domain': {
            'name': 'domain',
        },
        'message': {
            's': None,
        }
    }

    with pytest.raises(ValueError):
        EIP712Struct.from_message(message)


def test_extra_field_from_message_error():
    message = {
        'primaryType': 'Foo',
        'types': {
            'EIP712Domain': [{
                'name': 'name',
                'type': 'string',
            }],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'domain': {
            'name': 'domain',
        },
        'message': {
            's': 'x',
            'undeclared_field': 'y',
        }
    }

    with pytest.raises(KeyError):
        EIP712Struct.from_message(message)


def test_bytes_json_encoder():
    class Foo(EIP712Struct):
        b = Bytes(32)
    domain = make_domain(name='domain')

    bytes_val = os.urandom(32)
    foo = Foo(b=bytes_val)
    result = foo.to_message_json(domain)

    expected_substring = f'"b": "0x{bytes_val.hex()}"'
    assert expected_substring in result

    reconstructed = EIP712Struct.from_message(json.loads(result))
    assert reconstructed.domain == domain
    assert reconstructed.message == foo

    class UnserializableObject:
        pass
    obj = UnserializableObject()

    # Fabricate this failure case to test that the custom json encoder's fallback path works as expected.
    foo.values['b'] = obj
    with pytest.raises(TypeError, match='not JSON serializable'):
        foo.to_message_json(domain)


def test_wrong_domain_type():
    message = {  # invalid salt
        'types': {
            'EIP712Domain': [
                {'name': 'salt', 'type': 'string'}  # This is the wrong type
            ],
            'Foo': [{
                'name': 's',
                'type': 'string',
            }]
        },
        'primaryType': 'Foo',
        'domain': {'salt': 'rAnD0mstr1ng'},
        'message': {'s': 'foobar'},
    }
    with pytest.raises(ValueError):
        EIP712Struct.from_message(message)
