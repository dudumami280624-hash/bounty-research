"""Versioned public vulnerability lab catalog. These are offline source fixtures, not live targets."""
LABS = [
    {"id":"crytic-nssc","repository":"https://github.com/crytic/not-so-smart-contracts.git","ref":"master","kind":"historical-solidity","integration":"evm-replay"},
    {"id":"ethernaut","repository":"https://github.com/OpenZeppelin/ethernaut.git","ref":"master","kind":"evm-challenges","integration":"evm-replay"},
    {"id":"damn-vulnerable-defi","repository":"https://github.com/theredguild/damn-vulnerable-defi.git","ref":"v4.1.0","kind":"defi-challenges","integration":"forge-build"},
    {"id":"smartbugs-curated","repository":"https://github.com/smartbugs/smartbugs-curated.git","ref":"main","kind":"labeled-solidity","integration":"source-catalog"},
    {"id":"slither-detectors","repository":"https://github.com/crytic/slither.git","ref":"master","kind":"detector-reference","integration":"source-catalog"},
]
