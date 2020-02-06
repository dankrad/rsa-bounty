pragma solidity ^0.5.11;

contract RsaBounty {

    struct Challenge {
        bytes modulus;
        bool redeemed;
        uint bounty;
    }

    uint constant CLAIM_DELAY = 1 days;

    address owner;

    mapping(uint => Challenge) public challenges;
    uint public challenges_length;

    mapping(bytes32 => uint256) public claims;

    constructor () public payable {
        owner = msg.sender;
        // Test challenges
        challenges[0] = Challenge({
        modulus: hex"51e6945d1fe1c38b36664d4d8f9f105ea80af18a0eb2d830e69a32e8317f8f4c4e576c019e93232e95afba87ae3096492e459dbc5da3c52af371375b8929a4c65021db9ddb5099ccdcae5398b41b19c5ff6abd9d02c0c7281df453cb571e77ad",
        redeemed: false,
        bounty: 2 ether
        });

        challenges[1] = Challenge({
        modulus: hex"9de4c3579957110a3bfcbcde06caebac656da2a78cb3a0ad63470a143d617a847a004ec6bf69bfb3621d1eef5b6ac3c248f4623ac8f67db08dec222e72145f75122a0724daebd9eda4f714e95492e7033d086c443f105f545179dc976ea5afffdf37d67eb3c77601e1111a46d65974980cdaa7e51d082a9d127c3205d4dab057",
        redeemed: false,
        bounty: 4 ether
        });

        challenges[2] = Challenge({
        modulus: hex"66e9677ca625ef573e8caf740a8bf3ae7bcdf6207788152b0c0906c4538fd64a15ac10b54a3c82bdbfdaf1892adc79d205b9a95e9bd64fe453287db04fbda82327388154e5be7ae5126fad16fd467ba1d6dd1e00d6a8291e962ce5604b02485e7124b80c6a899871a627a0b32e0fb2f22e333380cd8219b82bbcd5790a53498b7150e9261774032ade4b016f00a62cfd262ad3268bb8e2755fbd6d8184157faedbcfe0c0e3a820fbcdd5c6e3a363e83cf1eb5ecacb5698668b9ee1acfadd0997",
        redeemed: false,
        bounty: 8 ether
        });

        challenges[3] = Challenge({
        modulus: hex"ab14a3e094faacbac8d8c03fb35a0ee1f11426ee2fa578c7f6c9649aad8a83e1859c9f3a369dbdea76574fd527aeb68a32364645a239cff4ecd2e8406e7f4b8f6f00baafd6d57da3e7ac5c87c26c738471d30a81097be0bae18f040ed2e8c27dd245b8a93cb05d10aa5cdcda3727c56a3d9bff776ff7dbf3a50385190957e637ded8ed48552cf2080983045e2aad681fe4bfcef58478bf37de5706f35079ebac88cad68a3a967f2e529cae849734279e4e537c84b9c93ef25f80b493990cea4d07bb035c6b7598b9e1aeb4829008e5a7d58597c7f693854b09dd8a622e8d8eb4bb39f1c83bdff133ae1d0f5579a99fc971d817222e3b9b2d482d4cc17a5bd57d",
        redeemed: false,
        bounty: 16 ether
        });

        challenges_length = 4;
    }


    // Expmod for small operands
    function expmod(uint base, uint e, uint m) public view returns (uint o) {
        assembly {
            // Get free memory pointer
            let p := mload(0x40)
            // Store parameters for the Expmod (0x05) precompile
            mstore(p, 0x20)             // Length of Base
            mstore(add(p, 0x20), 0x20)  // Length of Exponent
            mstore(add(p, 0x40), 0x20)  // Length of Modulus
            mstore(add(p, 0x60), base)  // Base
            mstore(add(p, 0x80), e)     // Exponent
            mstore(add(p, 0xa0), m)     // Modulus

            // Call 0x05 (EXPMOD) precompile
            if iszero(staticcall(sub(gas, 2000), 0x05, p, 0xc0, p, 0x20)) {
                revert(0, 0)
            }
            o := mload(p)
        }
    }

    // Expmod for bignum operands (encoded as bytes, only base and modulus)
    function bignum_expmod(bytes memory base, uint e, bytes memory m) public view returns (bytes memory o) {
        assembly {
            // Get free memory pointer
            let p := mload(0x40)

            // Get base length in bytes
            let bl := mload(base)
            // Get modulus length in bytes
            let ml := mload(m)

            // Store parameters for the Expmod (0x05) precompile
            mstore(p, bl)               // Length of Base
            mstore(add(p, 0x20), 0x20)  // Length of Exponent
            mstore(add(p, 0x40), ml)    // Length of Modulus
            // Use Identity (0x04) precompile to memcpy the base
            if iszero(staticcall(10000, 0x04, add(base, 0x20), bl, add(p, 0x60), bl)) {
                revert(0, 0)
            }
            mstore(add(p, add(0x60, bl)), e) // Exponent
            // Use Identity (0x04) precompile to memcpy the modulus
            if iszero(staticcall(10000, 0x04, add(m, 0x20), ml, add(add(p, 0x80), bl), ml)) {
                revert(0, 0)
            }
            
            // Call 0x05 (EXPMOD) precompile
            if iszero(staticcall(sub(gas, 2000), 0x05, p, add(add(0x80, bl), ml), add(p, 0x20), ml)) {
                revert(0, 0)
            }

            // Update free memory pointer
            mstore(0x40, add(add(p, ml), 0x20))

            // Store correct bytelength at p. This means that with the output
            // of the Expmod precompile (which is stored as p + 0x20)
            // there is now a bytes array at location p
            mstore(p, ml)

            // Return p
            o := p
        }
    }

    uint constant miller_rabin_checks = 28;

    // Use the Miller-Rabin test to check whether n>3, odd is a prime
    function miller_rabin_test(uint n) public view returns (bool) {
        require(n > 3);
        require(n & 0x1 == 1);
        uint d = n - 1;
        uint r = 0;
        while(d & 0x1 == 0) {
            d /= 2;
            r += 1;
        }
        for(uint i = 0; i < miller_rabin_checks; i++) {
            uint a = (uint256(sha256(abi.encodePacked(n, i))) % (n - 2)) + 2;
            uint x = expmod(a, d, n);
            if(x == 1 || x == n - 1) {
                continue;
            }
            bool check_passed = false;
            for(uint j = 0; j < r; j++) {
                x = mulmod(x, x, n);
                if(x == n - 1) {
                    check_passed = true;
                    break;
                }
            }
            if(!check_passed) {
                return false;
            }
        }
        return true;
    }

    // Need to submit a "claim" for a bounty 24 hrs before redeeming
    // This prevents front-running attacks
    function claim_bounty(bytes32 claim_hash) public {
        require(claims[claim_hash] == 0);
        claims[claim_hash] = block.timestamp + CLAIM_DELAY;
    }

    function max(uint a, uint b) private pure returns (uint) {
        return a > b ? a : b;
    }

    function bignum_getdigit(bytes memory x, uint i) private pure returns (uint8) {
        if(i >= x.length) {
            return 0;
        } else {
            return uint8(x[x.length - i - 1]);
        }
    }

    // Add two bignums encoded as bytes (very inefficient byte by byte method)
    function bignum_add(bytes memory x, bytes memory y) public pure returns (bytes memory) {
        uint newlength = max(x.length, y.length) + 1;
        bytes memory r = new bytes(newlength);
        uint carry = 0;
        for(uint i = 0; i < newlength; i++) {
            uint8 a = bignum_getdigit(x, i);
            uint8 b = bignum_getdigit(y, i);
            uint sum = uint(a) + uint(b) + carry;
            r[r.length - i - 1] = byte(uint8(sum));
            carry = sum >> 8;
            require(carry < 2);
        }
        return r;
    }

    // Compares two bignums encoded as bytes (very inefficient byte by byte method)
    function bignum_cmp(bytes memory x, bytes memory y) public pure returns (int) {
        int maxdigit = int(max(x.length, y.length) - 1);
        for(int i = maxdigit; i >= 0; i--) {
            uint8 a = bignum_getdigit(x, uint(i));
            uint8 b = bignum_getdigit(y, uint(i));
            if(a > b) {
                return 1;
            }
            if(b > a) {
                return -1;
            }
        }
        return 0;
    }
    
    // Mask used for hash to prime
    // Prime has to be the same as sha256(x) where mask is 1
    uint constant prime_mask = 0x7fff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_f000;

    function redeem_bounty(uint challenge_no, bytes memory x, bytes memory y, uint p) public {
        require(challenge_no < challenges_length);
        require(!challenges[challenge_no].redeemed);

        // Check claim has been made for this challenge
        bytes32 claim_hash = sha256(abi.encodePacked(challenge_no, x, y, p, bytes32(uint256(msg.sender))));
        require(claims[claim_hash] > 0);
        require(claims[claim_hash] < block.timestamp);

        // Check p is correct result for hash-to-prime
        require(p & prime_mask == uint(sha256(x)) & prime_mask);
        require(p > (1 << 255));
        require(miller_rabin_test(p));

        // Check 1 < x < m - 1
        require(bignum_cmp(x, hex"01") == 1);
        require(bignum_cmp(bignum_add(x, hex"01"), challenges[challenge_no].modulus) == -1);

        // Check y^p = x (mod m)
        bytes memory expmod_result = bignum_expmod(y, p, challenges[challenge_no].modulus);
        require(sha256(abi.encodePacked(expmod_result)) == sha256(abi.encodePacked(x)));
        
        challenges[challenge_no].redeemed = true;
        msg.sender.transfer(challenges[challenge_no].bounty);
    }
    
    
    function terminate_contract() public {
        require(msg.sender == owner);
        selfdestruct(msg.sender);
    }

}
