.PHONY: clean-pyc clean-build

all: contract/rsa_bounty.json

clean: clean-build

clean-build:
	rm contract/rsa_bounty.json

contract/rsa_bounty.json:
	solc --combined-json abi,bin contract/rsa_bounty.sol > contract/rsa_bounty.json

test:
	pipenv run pytest tests

test_install:
	pipenv shell
	pipenv install