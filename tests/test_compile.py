from contract.utils import (
    get_rsa_bounty_bytecode,
)
from vyper import (
    compiler,
)


def test_compile_rsa_bounty_contract():
    rsa_bounty_contract_code = get_rsa_bounty_bytecode()
