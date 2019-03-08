from eip712 import make_domain_separator


def test_domain_sep_create():
    domain_struct = make_domain_separator(name=True, salt=True)

    expected_result = 'EIP712Domain(string name,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result


def test_domain_sep_types():
    domain_struct = make_domain_separator(True, True, True, True, True)

    expected_result = 'EIP712Domain(string name,string version,uint256 chainId,address verifyingContract,bytes32 salt)'
    assert domain_struct.encode_type() == expected_result
