from eip712_structs import EIP712Struct, String, make_domain, struct_to_message, struct_from_message


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

    message, _ = struct_to_message(foo, domain)
    assert message == expected_result

    # Now test in reverse...
    new_struct, domain = struct_from_message(expected_result)
    assert new_struct.type_name == 'Foo'

    members_list = new_struct.get_members()
    assert len(members_list) == 1
    assert members_list[0][0] == 's'
    assert members_list[0][1].type_name == 'string'

    assert new_struct.get_data_value('s') == 'foobar'


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

    message, _ = struct_to_message(foo, domain)
    assert message == expected_result

    # And test in reverse...
    new_struct, new_domain = struct_from_message(expected_result)
    assert new_struct.type_name == 'Foo'

    members = new_struct.get_members()
    assert len(members) == 2
    assert members[0][0] == 's' and members[0][1].type_name == 'string'
    assert members[1][0] == 'bar' and members[1][1].type_name == 'Bar'

    bar_val = new_struct.get_data_value('bar')
    assert bar_val.type_name == 'Bar'
    assert bar_val.get_data_value('s') == 'bar'

    assert foo.hash_struct() == new_struct.hash_struct()
