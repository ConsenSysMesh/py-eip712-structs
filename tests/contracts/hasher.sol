pragma solidity >=0.4.0 <0.6.0;
pragma experimental ABIEncoderV2;

contract TestContract {
    struct Foo {
        string s;
        uint256 i;
    }

    bytes32 constant public Foo_TYPEHASH = keccak256(
        abi.encodePacked("Foo(string s,uint256 i)")
    );

    function hashStruct(Foo memory foo) public pure returns (bytes32 hash) {
        return keccak256(abi.encode(
            Foo_TYPEHASH,
            keccak256(abi.encodePacked(foo.s)),
            foo.i
        ));
    }

    function hashStructFromParams(string memory s, uint256 i) public pure returns (bytes32 hash) {
        Foo memory foo;
        foo.s = s;
        foo.i = i;
        return hashStruct(foo);
    }
}
