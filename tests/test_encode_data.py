import os
import random
import string

from eth_utils.crypto import keccak
import pytest

from eip712_structs import Address, Array, Boolean, Bytes, Int, String, Uint, EIP712Struct, make_domain


def signed_min_max(bits):
    min_val = (pow(2, bits) // 2) * -1
    max_val = (pow(2, bits) // 2) - 1
    return min_val, max_val


def unsigned_max(bits):
    return pow(2, bits) - 1


def test_encode_basic_types():
    class TestStruct(EIP712Struct):
        address = Address()
        boolean = Boolean()
        dyn_bytes = Bytes()
        bytes_1 = Bytes(1)
        bytes_32 = Bytes(32)
        int_32 = Int(32)
        int_256 = Int(256)
        string = String()
        uint_32 = Uint(32)
        uint_256 = Uint(256)

    values = dict()
    values['address'] = os.urandom(20)
    values['boolean'] = False
    values['dyn_bytes'] = os.urandom(random.choice(range(33, 100)))
    values['bytes_1'] = os.urandom(1)
    values['bytes_32'] = os.urandom(32)
    values['int_32'] = random.randint(*signed_min_max(32))
    values['int_256'] = random.randint(*signed_min_max(256))
    values['string'] = ''.join([random.choice(string.ascii_letters) for _ in range(100)])
    values['uint_32'] = random.randint(0, unsigned_max(32))
    values['uint_256'] = random.randint(0, unsigned_max(256))

    expected_data = list()
    expected_data.append(bytes(12) + values['address'])
    expected_data.append(bytes(32))
    expected_data.append(keccak(values['dyn_bytes']))
    expected_data.append(values['bytes_1'] + bytes(31))
    expected_data.append(values['bytes_32'])
    expected_data.append(values['int_32'].to_bytes(32, byteorder='big', signed=True))
    expected_data.append(values['int_256'].to_bytes(32, byteorder='big', signed=True))
    expected_data.append(keccak(text=values['string']))
    expected_data.append(values['uint_32'].to_bytes(32, byteorder='big', signed=False))
    expected_data.append(values['uint_256'].to_bytes(32, byteorder='big', signed=False))

    s = TestStruct(**values)
    encoded_data = s.encode_value()
    encoded_bytes = list()

    # Compare each byte range itself to find offenders
    for i in range(0, len(encoded_data), 32):
        encoded_bytes.append(encoded_data[i:i + 32])

    assert encoded_bytes == expected_data


def test_encode_array():
    class TestStruct(EIP712Struct):
        byte_array = Array(Bytes(32), 4)

    byte_array = [os.urandom(32) for _ in range(4)]

    s = TestStruct(byte_array=byte_array)
    assert s.encode_value() == keccak(b''.join(byte_array))


def test_encode_nested_structs():
    class SubStruct(EIP712Struct):
        s = String()

    class MainStruct(EIP712Struct):
        sub_1 = SubStruct
        sub_2 = String()
        sub_3 = SubStruct

    s1 = 'foo'
    s2 = 'bar'
    s3 = 'baz'

    sub_1 = SubStruct(s=s1)
    sub_3 = SubStruct(s=s3)

    s = MainStruct(
        sub_1=sub_1,
        sub_2=s2,
        sub_3=sub_3,
    )

    expected_encoded_vals = b''.join([sub_1.hash_struct(), keccak(text=s2), sub_3.hash_struct()])
    assert s.encode_value() == expected_encoded_vals


def test_data_dicts():
    class Foo(EIP712Struct):
        s = String()
        i = Int(256)

    class Bar(EIP712Struct):
        foo = Foo
        b = Bytes(1)

    bar = Bar(
        foo=Foo(
            s='hello',
            i=100,
        ),
        b=b'\xff'
    )

    expected_result = {
        'foo': {
            's': 'hello',
            'i': 100,
        },
        'b': b'\xff'
    }
    assert bar.data_dict() == expected_result


def test_signable_bytes():
    class Foo(EIP712Struct):
        s = String()
        i = Int(256)

    domain = make_domain(name='hello')
    foo = Foo(s='hello', i=1234)

    start_bytes = b'\x19\x01'
    exp_domain_bytes = keccak(domain.type_hash() + domain.encode_value())
    exp_struct_bytes = keccak(foo.type_hash() + foo.encode_value())

    sign_bytes = foo.signable_bytes(domain)
    assert sign_bytes[0:2] == start_bytes
    assert sign_bytes[2:34] == exp_domain_bytes
    assert sign_bytes[34:] == exp_struct_bytes


def test_none_replacement():
    class Foo(EIP712Struct):
        s = String()
        i = Int(256)

    foo = Foo(**{})
    encoded_val = foo.encode_value()
    assert len(encoded_val) == 64

    empty_string_hash = keccak(text='')
    assert encoded_val[0:32] == empty_string_hash
    assert encoded_val[32:] == bytes(32)


def test_validation_errors():
    bytes_type = Bytes(10)
    int_type = Int(8)    # -128 <= i < 128
    uint_type = Uint(8)  # 0 <= i < 256
    bool_type = Boolean()

    with pytest.raises(ValueError, match='bytes10 was given bytes with length 11'):
        bytes_type.encode_value(os.urandom(11))

    with pytest.raises(OverflowError, match='too big'):
        int_type.encode_value(128)
    with pytest.raises(OverflowError, match='too big'):
        int_type.encode_value(-129)

    with pytest.raises(OverflowError, match='too big'):
        uint_type.encode_value(256)
    assert uint_type.encode_value(0) == bytes(32)
    with pytest.raises(OverflowError, match='negative int to unsigned'):
        uint_type.encode_value(-1)

    assert bool_type.encode_value(True) == bytes(31) + b'\x01'
    assert bool_type.encode_value(False) == bytes(32)
    with pytest.raises(ValueError, match='Must be True or False.'):
        bool_type.encode_value(0)
    with pytest.raises(ValueError, match='Must be True or False.'):
        bool_type.encode_value(1)


def test_struct_eq():
    class Foo(EIP712Struct):
        s = String()
    foo = Foo(s='hello world')
    foo_copy = Foo(s='hello world')
    foo_2 = Foo(s='blah')


    assert foo != None
    assert foo != 'unrelated type'
    assert foo == foo
    assert foo is not foo_copy
    assert foo == foo_copy
    assert foo != foo_2

    def make_different_foo():
        # We want another struct defined with the same name but different member types
        class Foo(EIP712Struct):
            b = Bytes()
        return Foo

    def make_same_foo():
        # For good measure, recreate the exact same class and ensure they can still compare
        class Foo(EIP712Struct):
            s = String()
        return Foo

    OtherFooClass = make_different_foo()
    wrong_type = OtherFooClass(b=b'hello world')
    assert wrong_type != foo
    assert OtherFooClass != Foo

    SameFooClass = make_same_foo()
    right_type = SameFooClass(s='hello world')
    assert right_type == foo
    assert SameFooClass != Foo

    # Different name, same members
    class Bar(EIP712Struct):
        s = String()
    bar = Bar(s='hello world')
    assert bar != foo
