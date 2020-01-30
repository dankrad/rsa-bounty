from hashlib import (
    sha256,
)
from random import (
    Random,
)
import pytest
import eth_utils
from gmpy2 import is_prime, next_prime

# Make tests reproducible by setting the RNG seed, for comparing gas costs between runs.
rng = Random(123)
VALUES = [int(next_prime(rng.randint(0, 2**255 - 1))) for i in range(10)] \
    + [rng.randint(0, 2**255 - 1) * 2 + 1 for i in range(10)]

@pytest.mark.parametrize(
    'value', VALUES
)
def test_miller_rabin(rsa_bounty_contract,
                            w3,
                            value):
    call = rsa_bounty_contract.functions.miller_rabin_test(value)
    print(value.bit_length(), call.estimateGas())
    result = call.call()
    assert result == is_prime(value)
