import os
from eip712_structs import make_domain_separator
from eth_utils.crypto import keccak


def test_domain_sep_create():
    salt = os.urandom(32)
    domain_struct = make_domain_separator(name='name', salt=salt)

    expected_result = 'EIP712Domain(string name,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result

    expected_data = b''.join([keccak(text='name'), salt])
    assert domain_struct.encode_value() == expected_data


def test_domain_sep_types():
    salt = os.urandom(32)
    contract = os.urandom(20)

    domain_struct = make_domain_separator(name='name', version='version', chainId=1,
                                          verifyingContract=contract, salt=salt)

    encoded_data = [keccak(text='name'), keccak(text='version'), int(1).to_bytes(32, 'big', signed=False),
                    bytes(12) + contract, salt]

    expected_result = 'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result

    expected_data = b''.join(encoded_data)
    assert domain_struct.encode_value() == expected_data
