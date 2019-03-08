# EIP-712 Structs

"Structs" in here have nothing to do with the python module "struct".

## Basic Usage

Our desired struct:
```javascript
struct Message {
    address to;
    string contents;
}
```

Python representation:
```python
from eip712 import EIP712Struct, Address, String

class Message(EIP712Struct):
    to = Address()
    contents = String()
    
Message.encode_type()  # 'Mail(address to,string contents)'
```

#### A gotcha
The order attributes are declared matters! That order is preserved.

As an example, the following two structs are NOT the same.

```python
class Foo(EIP712Struct):
    a = String()
    b = String()

class Foo(EIP712Struct):
    b = String()
    a = String()
```

## Member Types

### Basic types
Basic types map to solidity types.

```python
from eip712 import Address, Boolean, Bytes, Int, String, Uint

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
dynamic_array = Array(X())     # X[] dynamic_array
static_array = Array(X(), 10)  # X[10] static_array
```

