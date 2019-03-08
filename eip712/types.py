class EIP712Type:
    def __init__(self, type_name: str):
        self.type_name = type_name


class Array(EIP712Type):
    def __init__(self, member_type: EIP712Type, fixed_length: int = 0):
        if fixed_length == 0:
            type_name = f'{member_type.type_name}[]'
        else:
            type_name = f'{member_type.type_name}[{fixed_length}]'
        super(Array, self).__init__(type_name)


class Address(EIP712Type):
    def __init__(self):
        super(Address, self).__init__('address')


class Boolean(EIP712Type):
    def __init__(self):
        super(Boolean, self).__init__('bool')


class Bytes(EIP712Type):
    def __init__(self, length: int = 0):
        if length == 0:
            # Special case: Length of 0 means a dynamic bytes type
            type_name = 'bytes'
        elif 1 <= length <= 32:
            type_name = f'bytes{length}'
        else:
            raise ValueError(f'Byte length must be between 1 or 32. Got: {length}')
        super(Bytes, self).__init__(type_name)


class Int(EIP712Type):
    def __init__(self, length: int):
        if length < 8 or length > 256 or length % 8 != 0:
            raise ValueError(f'Int length must be a multiple of 8, between 8 and 256. Got: {length}')
        super(Int, self).__init__(f'int{length}')


class String(EIP712Type):
    def __init__(self):
        super(String, self).__init__('string')


class Uint(EIP712Type):
    def __init__(self, length: int):
        if length < 8 or length > 256 or length % 8 != 0:
            raise ValueError(f'Uint length must be a multiple of 8, between 8 and 256. Got: {length}')
        super(Uint, self).__init__(f'uint{length}')

