import os
import json
import subprocess

DIR = os.path.dirname(__file__)


def get_rsa_bounty_contract_code():
    file_path = os.path.join(DIR, './rsa_bounty.sol')
    return open(file_path).read()


def get_rsa_bounty_bytecode():
    file_path = os.path.join(DIR, './rsa_bounty.sol')
    j = json.loads(subprocess.check_output(['solc', file_path, '--combined-json', 'abi,bin']))
    return list(j['contracts'].values())[0]
