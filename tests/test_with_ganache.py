import pytest

from requests.exceptions import ConnectionError
from web3 import HTTPProvider, Web3

from eip712_structs import EIP712Struct, String, Uint


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


# This must match the struct in tests/contracts/hasher.sol
class Foo(EIP712Struct):
    s = String()
    i = Uint(256)


def get_chain_hash(contract, s, i) -> bytes:
    result = contract.functions.hashStructFromParams(s, i).call()
    return result


def test_chain_hash_matches(contract):
    s = 'some string'
    i = 1234

    local_struct = Foo(s=s, i=i)
    our_hash = local_struct.hash_struct()

    their_hash = get_chain_hash(contract, s, i)
    assert our_hash == their_hash
