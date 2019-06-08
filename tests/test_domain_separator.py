import os

import pytest
from eth_utils.crypto import keccak

import eip712_structs
from eip712_structs import make_domain, EIP712Struct, String


@pytest.fixture
def default_domain_manager():
    # This fixture can be called to ensure we cleanup our default domain var before/after tests
    current_value = eip712_structs.default_domain
    eip712_structs.default_domain = None
    yield
    eip712_structs.default_domain = current_value


def test_domain_sep_create():
    salt = os.urandom(32)
    domain_struct = make_domain(name='name', salt=salt)

    expected_result = 'EIP712Domain(string name,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result

    expected_data = b''.join([keccak(text='name'), salt])
    assert domain_struct.encode_value() == expected_data

    with pytest.raises(ValueError, match='At least one argument must be given'):
        make_domain()


def test_domain_sep_types():
    salt = os.urandom(32)
    contract = os.urandom(20)

    domain_struct = make_domain(name='name', version='version', chainId=1,
                                verifyingContract=contract, salt=salt)

    encoded_data = [keccak(text='name'), keccak(text='version'), int(1).to_bytes(32, 'big', signed=False),
                    bytes(12) + contract, salt]

    expected_result = 'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result

    expected_data = b''.join(encoded_data)
    assert domain_struct.encode_value() == expected_data


def test_default_domain(default_domain_manager):
    assert eip712_structs.default_domain is None

    class Foo(EIP712Struct):
        s = String()
    foo = Foo(s='hello world')

    domain = make_domain(name='domain')
    other_domain = make_domain(name='other domain')

    # When neither methods provide a domain, expect a ValueError
    with pytest.raises(ValueError, match='Domain must be provided'):
        foo.to_message()
    with pytest.raises(ValueError, match='Domain must be provided'):
        foo.signable_bytes()

    # But we can still provide a domain explicitly
    explicit_msg = foo.to_message(domain)
    explicit_bytes = foo.signable_bytes(domain)

    # Setting it lets us forgo providing it
    eip712_structs.default_domain = domain
    implicit_msg = foo.to_message()
    implicit_bytes = foo.signable_bytes()

    # Either method should produce the same result
    assert implicit_msg == explicit_msg
    assert implicit_bytes == explicit_bytes

    # Using a different domain should not use any current default domain
    assert implicit_msg != foo.to_message(other_domain)
    assert implicit_bytes != foo.signable_bytes(other_domain)
