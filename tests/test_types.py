import pytest

from eip712 import Address, Array, Boolean, Bytes, Int, String, Uint


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
            clazz(0)


def test_int_validation():
    run_int_test(Int, 'int')


def test_uint_validation():
    run_int_test(Uint, 'uint')
