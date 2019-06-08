# API

### `class EIP712Struct`
#### Important methods
- `.to_message(domain: EIP712Struct)` - Convert the struct (and given domain struct) into the standard EIP-712 message structure.
- `.signable_bytes(domain: EIP712Struct)` - Get the standard EIP-712 bytes hash, suitable for signing.
- `.from_message(message_dict: dict)` **(Class method)** - Given a standard EIP-712 message dictionary (such as produced from `.to_message`), returns a NamedTuple containing the `message` and `domain` EIP712Structs.

#### Other stuff
- `.encode_value()` - Returns a `bytes` object containing the ordered concatenation of each members bytes32 representation.
- `.encode_type()` **(Class method)** - Gets the "signature" of the struct class. Includes nested structs too!
- `.type_hash()` **(Class method)** - The keccak256 hash of the result of `.encode_type()`.
- `.hash_struct()` - Gets the keccak256 hash of the concatenation of `.type_hash()` and `.encode_value()`
- `.get_data_value(member_name: str)` - Get the value of the given struct member
- `.set_data_value(member_name: str, value: Any)` - Set the value of the given struct member
- `.data_dict()` - Returns a dictionary with all data in this struct. Includes nested struct data, if exists.
- `.get_members()` **(Class method)** - Returns a dictionary mapping each data member's name to it's type.