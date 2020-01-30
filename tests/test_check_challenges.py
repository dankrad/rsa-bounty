from hashlib import (
    sha256,
)
from random import (
    randint,
)
import pytest
import eth_utils
from .challenges import challenges


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_check_challenge(rsa_bounty_contract,
                         w3,
                         challenge_no,
                         challenge):
    call = rsa_bounty_contract.functions.challenges(challenge_no)
    modulus, redeemed, bounty = call.call()
    assert not redeemed
    assert bounty == challenge["bounty"]
    assert int.from_bytes(modulus, "big") == challenge["modulus"]


def test_challenges_length(rsa_bounty_contract,
                           w3):
    call = rsa_bounty_contract.functions.challenges_length()
    num = call.call()
    assert num == len(challenges)
