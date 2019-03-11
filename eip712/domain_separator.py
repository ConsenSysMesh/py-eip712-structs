import eip712


def make_domain_separator(name=None, version=None, chainId=None, verifyingContract=None, salt=None):
    """Helper method to create the standard EIP712Domain struct for you.
    """
    class EIP712Domain(eip712.EIP712Struct):
        pass

    kwargs = dict()
    if name is not None:
        EIP712Domain.name = eip712.String()
        kwargs['name'] = name
    if version is not None:
        EIP712Domain.version = eip712.String()
        kwargs['version'] = version
    if chainId is not None:
        EIP712Domain.chainId = eip712.Uint(256)
        kwargs['chainId'] = chainId
    if verifyingContract is not None:
        EIP712Domain.verifyingContract = eip712.Address()
        kwargs['verifyingContract'] = verifyingContract
    if salt is not None:
        EIP712Domain.salt = eip712.Bytes(32)
        kwargs['salt'] = salt

    return EIP712Domain(**kwargs)
