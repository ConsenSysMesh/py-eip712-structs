import os
import pytest

from requests.exceptions import ConnectionError
from web3 import HTTPProvider, Web3

from eip712_structs import EIP712Struct, String, Uint, Int, Address, Boolean, Bytes


@pytest.fixture(scope='module')
def w3():
    client = Web3(HTTPProvider('http://localhost:8545'))
    client.eth.defaultAccount = client.eth.accounts[0]
    return client


@pytest.fixture(scope='module')
def contract(w3):
    base_path = 'tests/contracts/build/TestContract'
    with open(f'{base_path}.abi', 'r') as f:
        abi = f.read()
    with open(f'{base_path}.bin', 'r') as f:
        bin = f.read()

    tmp_contract = w3.eth.contract(abi=abi, bytecode=bin)
    deploy_hash = tmp_contract.constructor().transact()
    deploy_receipt = w3.eth.waitForTransactionReceipt(deploy_hash)

    deployed_contract = w3.eth.contract(abi=abi, address=deploy_receipt.contractAddress)
    return deployed_contract


def skip_this_module():
    client = Web3(HTTPProvider('http://localhost:8545'))
    try:
        client.eth.accounts
    except ConnectionError:
        return True
    return False


pytestmark = pytest.mark.skipif(skip_this_module(), reason='No accessible test chain.')


# These structs must match the struct in tests/contracts/hash_test_contract.sol
class Bar(EIP712Struct):
    bar_uint = Uint(256)


class Foo(EIP712Struct):
    s = String()
    u_i = Uint(256)
    s_i = Int(8)
    a = Address()
    b = Boolean()
    bytes_30 = Bytes(30)
    dyn_bytes = Bytes()
    bar = Bar


def get_chain_hash(contract, s, u_i, s_i, a, b, bytes_30, dyn_bytes, bar_uint) -> bytes:
    result = contract.functions.hashFooStructFromParams(s, u_i, s_i, a, b, bytes_30, dyn_bytes, bar_uint).call()
    return result


def test_encoded_types(contract):
    """Checks that the encoded types (and the respective hashes) of our structs match."""
    local_bar_sig = Bar.encode_type()
    remote_bar_sig = contract.functions.BarSig().call()
    assert local_bar_sig == remote_bar_sig

    local_foo_sig = Foo.encode_type()
    remote_foo_sig = contract.functions.FooSig().call()
    assert local_foo_sig == remote_foo_sig

    local_bar_hash = Bar.type_hash()
    remote_bar_hash = contract.functions.Bar_TYPEHASH().call()
    assert local_bar_hash == remote_bar_hash

    local_foo_hash = Foo.type_hash()
    remote_foo_hash = contract.functions.Foo_TYPEHASH().call()
    assert local_foo_hash == remote_foo_hash


def test_chain_hash_matches(contract):
    s = 'some string'
    u_i = 1234
    s_i = -7
    a = Web3.toChecksumAddress(f'0x{os.urandom(20).hex()}')
    b = True
    bytes_30 = os.urandom(30)
    dyn_bytes = os.urandom(50)

    bar_uint = 1337
    bar_struct = Bar(bar_uint=bar_uint)
    local_bar_hash = bar_struct.hash_struct()
    remote_bar_hash = contract.functions.hashBarStructFromParams(bar_uint).call()
    assert local_bar_hash == remote_bar_hash

    foo_struct = Foo(s=s, u_i=u_i, s_i=s_i, a=a, b=b, bytes_30=bytes_30, dyn_bytes=dyn_bytes, bar=bar_struct)
    local_foo_hash = foo_struct.hash_struct()
    remote_foo_hash = get_chain_hash(contract, s, u_i, s_i, a, b, bytes_30, dyn_bytes, bar_uint)
    assert local_foo_hash == remote_foo_hash
