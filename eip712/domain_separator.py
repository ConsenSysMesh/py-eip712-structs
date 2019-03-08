import eip712


def make_domain_separator(name=False, version=False, chainId=False, verifyingContract=False, salt=False):
    """Helper method to create the standard EIP712Domain struct for you.
    """
    class EIP712Domain(eip712.EIP712Struct):
        pass

    if name:
        EIP712Domain.name = eip712.String()
    if version:
        EIP712Domain.version = eip712.String()
    if chainId:
        EIP712Domain.chainId = eip712.Uint(256)
    if verifyingContract:
        EIP712Domain.verifyingContract = eip712.Address()
    if salt:
        EIP712Domain.salt = eip712.Bytes(32)

    return EIP712Domain
