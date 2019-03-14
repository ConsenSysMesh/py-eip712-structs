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
from eip712_structs import EIP712Struct, Address, String, make_domain, struct_to_dict

class Message(EIP712Struct):
    to = Address()
    contents = String()
    
enctyp = Message.encode_type()  # 'Mail(address to,string contents)'

msg = Message(to='0xdead...beef', contents='hello world')
msg.encode_data()  # The struct's data in encoded form

domain = make_domain(name='example')
msg_body, msg_hash = struct_to_dict(msg, domain)
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

#### Creating Messages and Hashing
Messages also require a domain struct. A helper method exists for this purpose.

```python
from eip712_structs import EIP712Struct, String, make_domain, struct_to_dict

domain = make_domain(name='my_domain')  # Also accepts kwargs: version, chainId, verifyingContract, salt

class Foo(EIP712Struct):
    bar = String()

foo = Foo(bar='baz')

message_dict, message_hash = struct_to_dict(foo, domain)
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

### Arrays
Arrays are also supported for the standard.

```python
array_member = Array(<item_type>[, <optional_length>])
```

- `<item_type>` - The basic type or struct that will live in the array
- `<optional_length>` - If given, the array is set to that length.

For example:
```python
dynamic_array = Array(X())      # X[] dynamic_array
static_array  = Array(X(), 10)  # X[10] static_array
```

## Development
Run tests:
- `pytest tests`
