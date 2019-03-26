import pytest

from eip712_structs import Address, Array, Boolean, Bytes, Int, String, Uint, EIP712Struct
from eip712_structs.types import from_solidity_type


def test_bytes_validation():
    bytes0 = Bytes()
    assert bytes0.type_name == 'bytes'

    bytes0 = Bytes(0)
    assert bytes0.type_name == 'bytes'

    for n in range(1, 33):
        bytes_n = Bytes(n)
        assert bytes_n.type_name == f'bytes{n}'

    with pytest.raises(ValueError):
        Bytes(33)


def run_int_test(clazz, base_name):
    for n in range(7, 258):
        if n % 8 == 0:
            int_n = clazz(n)
            assert int_n.type_name == f'{base_name}{n}'
        else:
            with pytest.raises(ValueError):
                clazz(n)

    for n in [-8, 0, 264]:
        with pytest.raises(ValueError):
            clazz(n)


def test_int_validation():
    run_int_test(Int, 'int')


def test_uint_validation():
    run_int_test(Uint, 'uint')


def test_arrays():
    assert Array(String()).type_name == 'string[]'
    assert Array(String(), 4).type_name == 'string[4]'

    assert Array(Bytes(17)).type_name == 'bytes17[]'
    assert Array(Bytes(17), 10).type_name == 'bytes17[10]'

    assert Array(Array(Uint(160))).type_name == 'uint160[][]'


def test_struct_arrays():
    class Foo(EIP712Struct):
        s = String()

    assert Array(Foo).type_name == 'Foo[]'
    assert Array(Foo, 10).type_name == 'Foo[10]'


def test_length_str_typing():
    # Ensure that if length is given as a string, it's typecast to int
    assert Array(String(), '5').fixed_length == 5
    assert Bytes('10').length == 10
    assert Int('128').length == 128
    assert Uint('128').length == 128


def test_from_solidity_type():
    assert from_solidity_type('address') == Address()
    assert from_solidity_type('bool') == Boolean()
    assert from_solidity_type('bytes') == Bytes()
    assert from_solidity_type('bytes32') == Bytes(32)
    assert from_solidity_type('int128') == Int(128)
    assert from_solidity_type('string') == String()
    assert from_solidity_type('uint256') == Uint(256)

    assert from_solidity_type('address[]') == Array(Address())
    assert from_solidity_type('address[10]') == Array(Address(), 10)
    assert from_solidity_type('bytes16[32]') == Array(Bytes(16), 32)

    # Sanity check that equivalency is working as expected
    assert from_solidity_type('bytes32') != Bytes(31)
    assert from_solidity_type('bytes16[32]') != Array(Bytes(16), 31)
    assert from_solidity_type('bytes16[32]') != Array(Bytes(), 32)
    assert from_solidity_type('bytes16[32]') != Array(Bytes(8), 32)
