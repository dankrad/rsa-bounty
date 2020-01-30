from random import (
    randint,
)
import re

import pytest

from contract.utils import (
    get_rsa_bounty_bytecode,
)
import eth_tester
from eth_tester import (
    EthereumTester,
    PyEVMBackend,
)
from vyper import (
    compiler,
)
from web3 import Web3
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)
from .challenges import challenges

@pytest.fixture
def tester():
    genesis_overrides = {'gas_limit': 10000000}
    custom_genesis_params = PyEVMBackend._generate_genesis_params(overrides=genesis_overrides)
    return EthereumTester(PyEVMBackend(genesis_parameters=custom_genesis_params))


@pytest.fixture
def a0(tester):
    return tester.get_accounts()[0]


@pytest.fixture
def w3(tester):
    web3 = Web3(EthereumTesterProvider(tester))
    return web3


@pytest.fixture
def rsa_bounty_contract(w3, tester):
    rsa_bounty_contract_json = get_rsa_bounty_bytecode()
    contract_abi = rsa_bounty_contract_json['abi']
    contract_bytecode = rsa_bounty_contract_json['bin']
    rsa = w3.eth.contract(abi=contract_abi,
                               bytecode=contract_bytecode)
    tx_hash = rsa.constructor().transact({"value": sum(c["bounty"] for c in challenges.values())})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    rsa_deployed = w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=contract_abi
    )
    return rsa_deployed


@pytest.fixture
def assert_tx_failed(tester):
    def assert_tx_failed(function_to_test, exception=eth_tester.exceptions.TransactionFailed):
        snapshot_id = tester.take_snapshot()
        with pytest.raises(exception):
            function_to_test()
        tester.revert_to_snapshot(snapshot_id)
    return assert_tx_failed
