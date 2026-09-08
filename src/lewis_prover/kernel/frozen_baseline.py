"""M1 integrity manifest of the complete administrative M0 freeze inputs.

Digests are SHA-256 of the raw Git blobs at ADMINISTRATIVE_FREEZE_COMMIT.
This module contains identities only, never executable formula/certificate
semantics. The YAML authorities remain the sole source of those semantics.
The manifest ships with the checker: repository_root cannot supply or update
it. A deliberate manifest/code change requires review of a new M1 candidate.
"""

from types import MappingProxyType

CERTIFIED_M0_COMMIT = "21117f3da827f873c3ed88b578a1681aabfca7ac"
ADMINISTRATIVE_FREEZE_COMMIT = "33e6a14a4b92534ea159868060576d1b45da9bb5"

FROZEN_INPUT_SHA256 = MappingProxyType({
    "spec/language.yaml": "716b244cc3b6ca35a5459c0b47c11d8680ebd4f1451d30bb8dc2076fa1aed47e",
    "spec/rules.yaml": "35eedb8177ce330f6827b05e9f1d33e30e1a6ec8412a461ea1690c385b9a5e23",
    "spec/schemas.yaml": "d7c3fcd5d581f8390345b95cacea9bc8a21a4beaa435919b089c252eab084df3",
    "spec/systems.yaml": "84d76ff732dabf24195257fccdb95437392eef21f530a9e852222774b237f2d1",
    "audit/m0/certified_ast_fingerprints.yaml": "7e7b124a0abc6bdad238d1393196872b9330fc4637e86b80b1a2ec1f32e85b45",
    "audit/m0/certificate_contract_lock.yaml": "5a2885f9665132617d77659c4c497f4b99872e05b2088d6d5ab6bcd556a0e4ba",
})
