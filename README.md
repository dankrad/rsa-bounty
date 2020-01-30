# RSA bounty smart contract

Smart contract for on-chain bounties for the RSA adaptive root problem.

The contract provides an interface to redeem a bounty that was set for RSA adaptive root problem (redeem_bounty method, for details on the bounties see [here](https://rsa.cash/bounties)). It is based on the Pocklington prime certificate hash-to-prime method 

 In order to redeem a bounty, it first has to be locked by providing a sha256 hash of the key (this is to prevent front running once someone has found a valid solution).

# Requirements

This project uses `pipenv`, https://docs.pipenv.org/en/latest/.

## Install

```bash
pipenv shell
pipenv install
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
