from hashlib import (
    sha256,
)
from random import (
    randint,
)
import pytest
import eth_utils
from .utils import (
    solve_bounty
)
from .challenges import challenges

HOUR = 3600
DAY = 24 * HOUR
CLAIM_DELAY = 1 * DAY


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_redeem(rsa_bounty_contract,
                a0,
                w3,
                tester,
                challenge_no,
                challenge):
    pre_contract_balance = w3.eth.getBalance(rsa_bounty_contract.address)
    pre_balance = w3.eth.getBalance(a0)

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no, \
        xbytes, 
        ybytes,
        p)
    print(call.estimateGas())
    
    tx_hash = call.transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    post_contract_balance = w3.eth.getBalance(rsa_bounty_contract.address)
    post_balance = w3.eth.getBalance(a0)
    assert pre_contract_balance - post_contract_balance == challenge["bounty"]
    assert post_balance - pre_balance > 0


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_redeem_modulus_minus_one(rsa_bounty_contract,
                a0,
                w3,
                tester,
                assert_tx_failed,
                challenge_no,
                challenge):

    x = challenge["modulus"] - 1
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_double_redeem(rsa_bounty_contract,
                       a0,
                       w3,
                       tester,
                       assert_tx_failed,
                       challenge_no,
                       challenge):
    pre_contract_balance = w3.eth.getBalance(rsa_bounty_contract.address)
    pre_balance = w3.eth.getBalance(a0)

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    tx_hash = call.transact()
    w3.eth.waitForTransactionReceipt(tx_hash)

    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_early_redeem(rsa_bounty_contract,
                      a0,
                      w3,
                      tester,
                      assert_tx_failed,
                      challenge_no,
                      challenge):
    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY - 1000)
    tester.mine_block()
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_redeem_no_claim(rsa_bounty_contract,
                        a0,
                        w3,
                        assert_tx_failed,
                        challenge_no,
                        challenge):

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0)

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_incorrect_redeem_root(rsa_bounty_contract,
                          a0,
                          w3,
                          tester,
                          assert_tx_failed,
                          challenge_no,
                          challenge):

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0, incorrect_root=True)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_incorrect_redeem_not_prime(rsa_bounty_contract,
                          a0,
                          w3,
                          tester,
                          assert_tx_failed,
                          challenge_no,
                          challenge):

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0, not_prime=True)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


@pytest.mark.parametrize(
    'challenge_no,challenge', challenges.items()
)
def test_incorrect_redeem_hash_to_prime(rsa_bounty_contract,
                          a0,
                          w3,
                          tester,
                          assert_tx_failed,
                          challenge_no,
                          challenge):

    x = randint(2, challenge["modulus"] - 2)
    y, p, xbytes, ybytes, bytes_to_hash = solve_bounty(x, challenge_no, challenge, a0, incorrect_hash_to_prime=True)

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256(bytes_to_hash).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)
    timestamp = w3.eth.getBlock('latest')['timestamp']
    tester.time_travel(timestamp + CLAIM_DELAY)
    tester.mine_block()
    tester.mine_block()

    call = rsa_bounty_contract.functions.redeem_bounty(challenge_no,
        xbytes, 
        ybytes,
        p)
    
    assert_tx_failed(call.transact)


def test_double_claim(rsa_bounty_contract,
                       a0,
                       w3,
                       tester,
                       assert_tx_failed):

    claim_call = rsa_bounty_contract.functions.claim_bounty(sha256((0).to_bytes(32, "big")
        + bytes.fromhex(a0[2:]).rjust(32, b"\0")).digest())
    lc_tx_hash = claim_call.transact()
    lc_tx_receipt = w3.eth.waitForTransactionReceipt(lc_tx_hash)

    assert_tx_failed(claim_call.transact)
