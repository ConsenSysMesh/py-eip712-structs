import pytest

from eip712_structs import Address, Array, Boolean, Bytes, Int, String, Uint


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
