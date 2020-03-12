from gmpy2 import gcdext, powmod, next_prime, mpz, is_prime, gcd
from hashlib import sha256
from operator import mul
from functools import reduce


def modular_root(m, factors, x, p):
    multiplicative_group_order = reduce(mul, [x - 1 for x in factors])
    _, p_inv, _ = gcdext(p, multiplicative_group_order)
    return int(powmod(x, p_inv, m))


def hash_to_prime(x, incorrect_hash_to_prime=False):
    prime_mask = 0x7fff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff_f000

    xbytes = x.to_bytes(((x.bit_length() + 7) // 8) * 1, "big")
    h = int.from_bytes(sha256(xbytes).digest(), "big")
    h &= prime_mask
    h |= 2**255
    if incorrect_hash_to_prime:
        h ^= 0xff00_0000_0000    
    h = int(next_prime(h))
    assert h > 2**255
    assert h < 2**256
    return h


def solve_bounty(x, challenge_no, challenge, a0, incorrect_root = False, incorrect_hash_to_prime = False, not_prime = False):
    p = hash_to_prime(x, incorrect_hash_to_prime)
    if not_prime:
        multiplicative_group_order = reduce(mul, [x - 1 for x in challenge["factors"]])
        while is_prime(p) or gcd(p, multiplicative_group_order) > 1:
            p += 2
    y = modular_root(challenge["modulus"], challenge["factors"], x, p)

    if incorrect_root:
        y += 1
    else:
        assert powmod(y, p, challenge["modulus"]) == x

    xbytes = x.to_bytes(((challenge["modulus"].bit_length() + 7) // 8) * 1, "big")
    ybytes = y.to_bytes(((challenge["modulus"].bit_length() + 7) // 8) * 1, "big")

    bytes_to_hash = challenge_no.to_bytes(32, "big") + xbytes + \
                    ybytes + \
                    p.to_bytes(32, "big") + \
                    bytes.fromhex(a0[2:]).rjust(32, b"\0")
    
    return y, p, xbytes, ybytes, bytes_to_hash