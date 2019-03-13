from collections import OrderedDict, defaultdict
from typing import List, Tuple

from eth_utils.crypto import keccak

from eip712_structs.types import EIP712Type, from_solidity_type


class OrderedAttributesMeta(type):
    """Metaclass to ensure struct attribute order is preserved.
    """
    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()


class _EIP712StructTypeHelper(EIP712Type, metaclass=OrderedAttributesMeta):
    """Helper class to map the more complex struct type to the basic type interface.
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.type_name = cls.__name__


class EIP712Struct(_EIP712StructTypeHelper):
    def __init__(self, **kwargs):
        super(EIP712Struct, self).__init__(self.type_name)
        members = self.get_members()
        self.values = dict()
        for name, typ in members:
            value = kwargs.get(name)
            if isinstance(value, dict):
                value = typ(**value)
            self.values[name] = value

    def encode_value(self, value=None):
        encoded_values = [typ.encode_value(self.values[name]) for name, typ in self.get_members()]
        return b''.join(encoded_values)

    def encode_data(self):
        return self.encode_value()

    def get_data_value(self, name):
        return self.values.get(name)

    def set_data_value(self, name, value):
        if name in self.values:
            self.values[name] = value

    def data_dict(self):
        result = dict()
        for k, v in self.values.items():
            if isinstance(v, EIP712Struct):
                result[k] = v.data_dict()
            else:
                result[k] = v
        return result

    @classmethod
    def _encode_type(cls, resolve_references: bool) -> str:
        member_sigs = [f'{typ.type_name} {name}' for name, typ in cls.get_members()]
        struct_sig = f'{cls.type_name}({",".join(member_sigs)})'

        if resolve_references:
            reference_structs = set()
            cls._gather_reference_structs(reference_structs)
            sorted_structs = sorted(list(s for s in reference_structs if s != cls), key=lambda s: s.type_name)
            for struct in sorted_structs:
                struct_sig += struct._encode_type(resolve_references=False)
        return struct_sig

    @classmethod
    def _gather_reference_structs(cls, struct_set):
        structs = [m[1] for m in cls.get_members() if isinstance(m[1], type) and issubclass(m[1], EIP712Struct)]
        for struct in structs:
            if struct not in struct_set:
                struct_set.add(struct)
                struct._gather_reference_structs(struct_set)

    @classmethod
    def encode_type(cls):
        return cls._encode_type(True)

    @classmethod
    def type_hash(cls):
        return keccak(text=cls.encode_type())

    def hash_struct(self):
        return keccak(b''.join([self.type_hash(), self.encode_data()]))

    @classmethod
    def get_members(cls) -> List[Tuple[str, EIP712Type]]:
        members = [m for m in cls.__dict__.items() if isinstance(m[1], EIP712Type)
                   or (isinstance(m[1], type) and issubclass(m[1], EIP712Struct))]
        return members


def struct_to_json(domain: EIP712Struct, primary_struct: EIP712Struct):
    structs = {domain, primary_struct}
    primary_struct._gather_reference_structs(structs)

    # Build type dictionary
    types = dict()
    for struct in structs:
        members_json = [{
            'name': m[0],
            'type': m[1].type_name,
        } for m in struct.get_members()]
        types[struct.type_name] = members_json

    result = {
        'primaryType': primary_struct.type_name,
        'types': types,
        'domain': domain.data_dict(),
        'message': primary_struct.data_dict(),
    }

    typed_data_hash = keccak(b'\x19\x01' + domain.type_hash() + primary_struct.type_hash())

    return result, typed_data_hash


def struct_from_json(json):
    structs = dict()
    unfulfilled_struct_params = defaultdict(list)

    for type_name in json['types']:
        # Dynamically construct struct class from JSON
        StructFromJSON = type(type_name, (EIP712Struct,), {})

        for member in json['types'][type_name]:
            # Either a basic solidity type is set, or None if referring to a reference struct (we'll fill that later)
            member_name = member['name']
            member_sol_type = from_solidity_type(member['type'])
            setattr(StructFromJSON, member_name, member_sol_type)
            if member_sol_type is None:
                unfulfilled_struct_params[type_name].append((member_name, member['type']))

        structs[type_name] = StructFromJSON

    for struct_name, unfulfilled_member_names in unfulfilled_struct_params.items():
        struct_class = structs[struct_name]
        for name, type_name in unfulfilled_member_names:
            ref_struct = structs[type_name]
            setattr(struct_class, name, ref_struct)

    primary_struct = structs[json['primaryType']]
    return primary_struct(**json['message'])
