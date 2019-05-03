import re
from typing import Any, Union, Type

from eth_utils.crypto import keccak
from eth_utils.conversions import to_int


class EIP712Type:
    """The base type for members of a struct.
    """
    def __init__(self, type_name: str, none_val: Any):
        self.type_name = type_name
        self.none_val = none_val

    def encode_value(self, value) -> bytes:
        if value is None:
            return self._encode_value(self.none_val)
        else:
            return self._encode_value(value)

    def _encode_value(self, value) -> bytes:
        """Given a value, verify it and convert into the format required by the spec.

        :param value: A correct input value for the implemented type.
        :return: A 32-byte object containing encoded data
        """
        pass

    def __eq__(self, other):
        self_type = getattr(self, 'type_name')
        other_type = getattr(other, 'type_name')

        return self_type is not None and self_type == other_type

    def __hash__(self):
        return hash(self.type_name)


class Array(EIP712Type):
    def __init__(self, member_type: Union[EIP712Type, Type[EIP712Type]], fixed_length: int = 0):
        fixed_length = int(fixed_length)
        if fixed_length == 0:
            type_name = f'{member_type.type_name}[]'
        else:
            type_name = f'{member_type.type_name}[{fixed_length}]'
        self.member_type = member_type
        self.fixed_length = fixed_length
        super(Array, self).__init__(type_name, [])

    def _encode_value(self, value):
        encoder = self.member_type
        encoded_values = [encoder.encode_value(v) for v in value]
        return keccak(b''.join(encoded_values))


class Address(EIP712Type):
    def __init__(self):
        super(Address, self).__init__('address', 0)

    def _encode_value(self, value):
        # Some smart conversions - need to get an address as an int
        if isinstance(value, bytes):
            v = to_int(value)
        elif isinstance(value, str):
            v = to_int(hexstr=value)
        else:
            v = value
        return Uint(160).encode_value(v)


class Boolean(EIP712Type):
    def __init__(self):
        super(Boolean, self).__init__('bool', False)

    def _encode_value(self, value):
        if value is False:
            return Uint(256).encode_value(0)
        elif value is True:
            return Uint(256).encode_value(1)
        else:
            raise ValueError(f'Must be True or False. Got: {value}')


class Bytes(EIP712Type):
    def __init__(self, length: int = 0):
        length = int(length)
        if length == 0:
            # Special case: Length of 0 means a dynamic bytes type
            type_name = 'bytes'
        elif 1 <= length <= 32:
            type_name = f'bytes{length}'
        else:
            raise ValueError(f'Byte length must be between 1 or 32. Got: {length}')
        self.length = length
        super(Bytes, self).__init__(type_name, b'')

    def _encode_value(self, value):
        if self.length == 0:
            return keccak(value)
        else:
            if len(value) > self.length:
                raise ValueError(f'{self.type_name} was given bytes with length {len(value)}')
            padding = bytes(32 - len(value))
            return value + padding


class Int(EIP712Type):
    def __init__(self, length: int):
        length = int(length)
        if length < 8 or length > 256 or length % 8 != 0:
            raise ValueError(f'Int length must be a multiple of 8, between 8 and 256. Got: {length}')
        self.length = length
        super(Int, self).__init__(f'int{length}', 0)

    def _encode_value(self, value: int):
        value.to_bytes(self.length // 8, byteorder='big', signed=True)  # For validation
        return value.to_bytes(32, byteorder='big', signed=True)


class String(EIP712Type):
    def __init__(self):
        super(String, self).__init__('string', '')

    def _encode_value(self, value):
        return keccak(text=value)


class Uint(EIP712Type):
    def __init__(self, length: int):
        length = int(length)
        if length < 8 or length > 256 or length % 8 != 0:
            raise ValueError(f'Uint length must be a multiple of 8, between 8 and 256. Got: {length}')
        self.length = length
        super(Uint, self).__init__(f'uint{length}', 0)

    def _encode_value(self, value: int):
        value.to_bytes(self.length // 8, byteorder='big', signed=False)  # For validation
        return value.to_bytes(32, byteorder='big', signed=False)


solidity_type_map = {
    'address': Address,
    'bool': Boolean,
    'bytes': Bytes,
    'int': Int,
    'string': String,
    'uint': Uint,
}


def from_solidity_type(solidity_type: str):
    """Convert a string into the EIP712Type implementation. Basic types only."""
    pattern = r'([a-z]+)(\d+)?(\[(\d+)?\])?'
    match = re.match(pattern, solidity_type)

    if match is None:
        return None

    type_name = match.group(1)
    opt_len = match.group(2)
    is_array = match.group(3)
    array_len = match.group(4)

    if type_name not in solidity_type_map:
        return None

    base_type = solidity_type_map[type_name]
    if opt_len:
        type_instance = base_type(int(opt_len))
    else:
        type_instance = base_type()

    if is_array:
        if array_len:
            result = Array(type_instance, int(array_len))
        else:
            result = Array(type_instance)
        return result
    else:
        return type_instance
