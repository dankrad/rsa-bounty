# RSA bounty smart contract

Smart contract for on-chain bounties for the RSA adaptive root problem.

The contract provides an interface to redeem a bounty that was set for RSA adaptive root problem (redeem_bounty method, for details on the bounties see [here](https://rsa.cash/bounties)).

In order to redeem a bounty, it first has to be locked by providing a sha256 hash of the solution (this is to prevent front running once someone has found a valid solution).

# Redeeming a bounty

If you believe that you have an efficient algorithm to find adaptive roots in RSA groups, then you can prove this by calling this contract and claiming some Ether. A valid proof for a modulus m consists of the following:

1. Any number x that satisfies 1 < x < m - 1
2. A prime p that is x "hashed to a prime". To make verification easier and feasible in a smart comtract, the hash to prime algorithm is not unique, and any p satisfying the following conditions is considered valid:
 * Let h = sha256(x) be the hash of x (as a big-endian byte string)
 * p has to be equal to h except for the most significant bit and the 12 least significant bits
 * The most significant bit of p must be 1
 * p must be a prime
3. A number y that satisfies y^p = x (mod m)

If you have found such a solution, you must first submit a "claim" to it. This is necessary so that you can't be frontrun when you send the transaction to your bounty. You do this by submitting the hash of your solution. The hash is the sha256 value of: 
 * the challenge number (as a 32-byte big-endian number)
 * x (bytes, big-endian)
 * y (bytes, big-endian)
 * p (as a 32-byte big-endian number)
 * your Ethereum account (zero-padded to 32 bytes)

You submit a claim by calling the function
 * claim_bounty(bytes32 claim_hash)
Then after 24 hours, you call
 * redeem_bounty(uint challenge_no, bytes memory x, bytes memory y, uint p)
to redeem

For more concrete examples, you should check tests/test_redeem.py for a concrete implementation of redeeming a bounty.

# Requirements

This project uses `pipenv`, https://docs.pipenv.org/en/latest/.

## Install

A working solidity compiler (solc version 0.5.11) is required.

```bash
make test_install
```

## Compile

```bash
solc contract/rsa_bounty.sol
```

## Run tests

```bash
make test_install
make test
```

## Run with gas cost estimates

To enable debug printing, run pytest with extra flags:

```bash
pipenv run pytest -s -v -k test_redeem
```