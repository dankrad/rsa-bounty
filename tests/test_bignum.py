from hashlib import (
    sha256,
)
from random import (
    Random,
)

import pytest
import eth_utils
from gmpy2 import powmod, cmp

# Make tests reproducible by setting the RNG seed, for comparing gas costs between runs.
rng = Random(123)
VALUES_expmod = [(rng.randint(0, 2**256 - 1), rng.randint(0, 2**256 - 1), rng.randint(0, 2**100 - 1)) for i in range(10)]
VALUES_bignum_expmod = [(rng.randint(0, 2**2048 - 1), rng.randint(0, 2**256 - 1), rng.randint(0, 2**2048 - 1)) for i in range(10)]
VALUES_bignum = [(rng.randint(0, 2**2048 - 1), rng.randint(0, 2**2048 - 1)) for i in range(10)] + \
    [(rng.randint(0, 2**1311 - 1), rng.randint(0, 2**1715 - 1)) for i in range(10)] + \
    [(rng.randint(0, 2**123 - 1), rng.randint(0, 2**777 - 1)) for i in range(10)] + \
    [(rng.randint(0, 2**5 - 1), rng.randint(0, 2**51 - 1)) for i in range(10)] + \
    [(rng.randint(0, 2**2048 - 1), 1) for i in range(10)] + \
    [(x, x) for x in [rng.randint(0, 2**2048 - 1) for i in range(10)]]


@pytest.mark.parametrize(
    'value0,value1,value2', VALUES_expmod
)
def test_expmod(rsa_bounty_contract,
                            w3,
                            value0,
                            value1,
                            value2):
    call = rsa_bounty_contract.functions.expmod(value0, value1, value2)
    print(max(value0.bit_length(), value1.bit_length()), call.estimateGas())
    result = call.call()
    assert result == powmod(value0, value1, value2)


@pytest.mark.parametrize(
    'value0,value1,value2', VALUES_bignum_expmod
)
def test_bignum_expmod(rsa_bounty_contract,
                            w3,
                            value0,
                            value1,
                            value2):
    call = rsa_bounty_contract.functions.bignum_expmod(
        value0.to_bytes((value0.bit_length() + 7) // 8, "big"),
        value1,
        value2.to_bytes((value2.bit_length() + 7) // 8, "big"))
    print(max(value0.bit_length(), value2.bit_length()), call.estimateGas())
    result = call.call()
    assert int.from_bytes(result, "big") == powmod(value0, value1, value2)


@pytest.mark.parametrize(
    'value0,value1', VALUES_bignum
)
def test_bignum_cmp(rsa_bounty_contract,
                            w3,
                            value0,
                            value1):
    call = rsa_bounty_contract.functions.bignum_cmp(
        value0.to_bytes((value0.bit_length() + 7) // 8, "big"),
        value1.to_bytes((value1.bit_length() + 7) // 8, "big"))
    print(max(value0.bit_length(), value1.bit_length()), call.estimateGas())
    result = call.call()
    assert result == cmp(value0, value1)


@pytest.mark.parametrize(
    'value0,value1', VALUES_bignum
)
def test_bignum_add(rsa_bounty_contract,
                            w3,
                            value0,
                            value1):
    call = rsa_bounty_contract.functions.bignum_add(
        value0.to_bytes((value0.bit_length() + 7) // 8, "big"),
        value1.to_bytes((value1.bit_length() + 7) // 8, "big"))
    print(max(value0.bit_length(), value1.bit_length()), call.estimateGas())
    result = call.call()
    assert int.from_bytes(result, "big") == value0 + value1