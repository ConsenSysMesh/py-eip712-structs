# EIP-712 Structs

A python interface for simple EIP-712 struct construction.

In this module, a "struct" is structured data as defined in the standard.
It is not the same as the Python Standard Library's struct (e.g., `import struct`).

Read the proposal:<br/>
https://github.com/ethereum/EIPs/blob/master/EIPS/eip-712.md

## Install
```bash
pip install eip712-structs
```

## Basic Usage

Our desired struct:
```
struct Message {
    address to;
    string contents;
}
```

Python representation:
```python
from eip712_structs import EIP712Struct, Address, String, make_domain, struct_to_message

class Message(EIP712Struct):
    to = Address()
    contents = String()
    
enctyp = Message.encode_type()  # 'Mail(address to,string contents)'

msg = Message(to='0xdead...beef', contents='hello world')
msg.encode_data()  # The struct's data in encoded form

domain = make_domain(name='example')
msg_body, signable_bytes = struct_to_message(msg, domain)

# msg_body is a standardized dict with keys primaryType, types, domain, and message
# suitable for converting to JSON for making requests

# `signable bytes` is a deterministic bytes representation of the struct
# Suitable for hashing or signing
#   bytes 0-1: b'\x19\x01'
#   bytes 2-33: domain separator (hash of domain type and data)
#   bytes 34-65: hash of struct type and data
```

#### Dynamic construction
Attributes may be added dynamically as well. This may be necessary if you
want to use a reserved keyword like `from`.

```python
class Message(EIP712Struct):
    pass

Message.to = Address()
setattr(Message, 'from', Address())
```

#### The domain separator
Messages also require a domain struct. A helper method exists for this purpose.
All values to the `make_domain()`
function are optional - but at least one must be defined. If omitted, the resulting
domain struct's definition leaves out the parameter entirely.

The full signature: <br/>
`make_domain(name: string, version: string, chainId: uint256, verifyingContract: address, salt: bytes32)`

```python
from eip712_structs import EIP712Struct, String, make_domain, struct_to_message

domain = make_domain(name='my_domain')

class Foo(EIP712Struct):
    bar = String()

foo = Foo(bar='baz')

message_dict, message_hash = struct_to_message(foo, domain)
```


## Member Types

### Basic types
EIP712's basic types map directly to solidity types.

```python
from eip712_structs import Address, Boolean, Bytes, Int, String, Uint

Address()  # Solidity's 'address'
Boolean()  # 'bool'
Bytes()    # 'bytes'
Bytes(N)   # 'bytesN' - N must be an int from 1 through 32
Int(N)     # 'intN' - N must be a multiple of 8, from 8 to 256
String()   # 'string'
Uint(N)    # 'uintN' - N must be a multiple of 8, from 8 to 256
```

Use like:
```python
class Foo(EIP712Struct):
    member_name_0 = Address()
    member_name_1 = Bytes(5)
    # ...etc
```

### Struct references
In addition to holding basic types, EIP712 structs may also hold other structs!
Usage is almost the same - the difference is you don't "instantiate" the class.

Example:
```python
class Dog(EIP712Struct):
    name = String()
    breed = String()

class Person(EIP712Struct):
    name = String()
    dog = Dog  # Take note - no parentheses!

Dog.encode_type()     # Dog(string name,string breed)
Person.encode_type()  # Person(string name,Dog dog)Dog(string name,string breed)
```

Instantiating the structs with nested values may be done like:

```python
# Method one: set it to a struct
dog = Dog(name='Mochi', breed='Corgi')
person = Person(name='Ed', dog=dog)

# Method two: set it to a dict - the underlying struct is built for you
person = Person(
    name='Ed',
    dog={
        'name': 'Mochi',
        'breed': 'Corgi',
    }
)
```

### Arrays
Arrays are also supported for the standard.

```python
array_member = Array(<item_type>[, <optional_length>])
```

- `<item_type>` - The basic type or struct that will live in the array
- `<optional_length>` - If given, the array is set to that length.

For example:
```python
dynamic_array = Array(String())      # String[] dynamic_array
static_array  = Array(String(), 10)  # String[10] static_array
struct_array = Array(MyStruct, 10)   # MyStruct[10] - again, don't instantiate structs like the basic types
```

## Development
Run tests:
- `pytest tests`
