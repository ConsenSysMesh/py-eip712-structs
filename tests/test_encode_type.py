from eip712 import Address, EIP712Struct, String


def test_empty_struct():
    class Empty(EIP712Struct):
        pass

    assert Empty.encode_type() == 'Empty()'


def test_simple_struct():
    class Person(EIP712Struct):
        name = String()
        addr = Address()

    expected_result = 'Person(string name,address addr)'
    assert Person.encode_type() == expected_result


def test_struct_with_reference():
    class Person(EIP712Struct):
        name = String()
        addr = Address()

    class Mail(EIP712Struct):
        source = Person
        dest = Person
        content = String()

    expected_result = 'Mail(Person source,Person dest,string content)Person(string name,address addr)'
    assert Mail.encode_type() == expected_result


def test_nested_reference():
    class C(EIP712Struct):
        s = String()

    class B(EIP712Struct):
        s = String()
        c = C

    class A(EIP712Struct):
        s = String()
        b = B

    expected_result = 'A(string s,B b)B(string s,C c)C(string s)'
    assert A.encode_type() == expected_result


def test_reference_ordering():
    # The "main" struct is always first. Then the rest are ordered alphabetically.
    class B(EIP712Struct):
        s = String()

    class C(EIP712Struct):
        s = String()
        b = B

    class A(EIP712Struct):
        s = String()
        c = C

    expected_result = 'A(string s,C c)B(string s)C(string s,B b)'
    assert A.encode_type() == expected_result

    class Z(EIP712Struct):
        s = String()
        a = A

    expected_result = 'Z(string s,A a)' + expected_result
    assert Z.encode_type() == expected_result


def test_circular_reference():
    class C(EIP712Struct):
        # Must define A before we can reference it
        pass

    class B(EIP712Struct):
        c = C

    class A(EIP712Struct):
        b = B

    C.a = A

    a_sig = 'A(B b)'
    b_sig = 'B(C c)'
    c_sig = 'C(A a)'

    expected_result_a = f'{a_sig}{b_sig}{c_sig}'
    expected_result_b = f'{b_sig}{a_sig}{c_sig}'
    expected_result_c = f'{c_sig}{a_sig}{b_sig}'

    assert A.encode_type() == expected_result_a
    assert B.encode_type() == expected_result_b
    assert C.encode_type() == expected_result_c

