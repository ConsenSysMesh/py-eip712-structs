pragma solidity >=0.5.0 <0.6.0;
pragma experimental ABIEncoderV2;


contract TestContract {
    /********************
     * Constant Members *
     ********************/
    struct Bar {
        uint256 bar_uint;
    }

    struct Foo {
        string s;
        uint256 u_i;
        int8 s_i;
        address a;
        bool b;
        bytes30 bytes_30;
        bytes dyn_bytes;
        Bar bar;
    }

    string constant public BarSig = "Bar(uint256 bar_uint)";
    string constant public FooSig = "Foo(string s,uint256 u_i,int8 s_i,address a,bool b,bytes30 bytes_30,bytes dyn_bytes,Bar bar)Bar(uint256 bar_uint)";

    bytes32 constant public Bar_TYPEHASH = keccak256(
        abi.encodePacked("Bar(uint256 bar_uint)")
    );
    bytes32 constant public Foo_TYPEHASH = keccak256(
        abi.encodePacked("Foo(string s,uint256 u_i,int8 s_i,address a,bool b,bytes30 bytes_30,bytes dyn_bytes,Bar bar)Bar(uint256 bar_uint)")
    );

    /******************/
    /* Hash Functions */
    /******************/
    function hashBarStruct(Bar memory bar) public pure returns (bytes32) {
        return keccak256(abi.encode(
            Bar_TYPEHASH,
            bar.bar_uint
        ));
    }

    function hashFooStruct(Foo memory foo) public pure returns (bytes32) {
        return keccak256(abi.encode(
            Foo_TYPEHASH,
            keccak256(abi.encodePacked(foo.s)),
            foo.u_i,
            foo.s_i,
            foo.a,
            foo.b,
            foo.bytes_30,
            keccak256(abi.encodePacked(foo.dyn_bytes)),
            hashBarStruct(foo.bar)
        ));
    }

    function hashBarStructFromParams(
        uint256 bar_uint
    ) public pure returns (bytes32) {
        Bar memory bar;
        bar.bar_uint = bar_uint;
        return hashBarStruct(bar);
    }

    function hashFooStructFromParams(
        string memory s,
        uint256 u_i,
        int8 s_i,
        address a,
        bool b,
        bytes30 bytes_30,
        bytes memory dyn_bytes,
        uint256 bar_uint
    ) public pure returns (bytes32) {
        // Construct Foo struct with basic types
        Foo memory foo;
        foo.s = s;
        foo.u_i = u_i;
        foo.s_i = s_i;
        foo.a = a;
        foo.b = b;
        foo.bytes_30 = bytes_30;
        foo.dyn_bytes = dyn_bytes;

        // Construct Bar struct and add it to Foo
        Bar memory bar;
        bar.bar_uint = bar_uint;
        foo.bar = bar;

        return hashFooStruct(foo);
    }
}
