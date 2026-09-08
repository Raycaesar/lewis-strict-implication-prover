"""Fail-closed loader for the certified and frozen M0 specification."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from lewis_prover.errors import (
    FrozenContractError,
    FrozenSpecBasisError,
    FrozenSpecFingerprintError,
    FrozenSpecFormatError,
    FrozenSpecIntegrityError,
    FrozenSpecStatusError,
    FrozenSpecVersionError,
)

from .frozen_baseline import ADMINISTRATIVE_FREEZE_COMMIT, FROZEN_INPUT_SHA256
from .model import FrozenBasis, FrozenSpec, deep_freeze

PROJECT = "lewis-strict-implication-prover"
FROZEN_STATUS = "frozen_m0"
FROZEN_SPEC_VERSION = "0.6"

_COMPONENTS = ("language", "rules", "schemas", "systems")
_SCHEMA_IDS = frozenset(
    {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A8", "C10", "C11", "C12"}
)
_DEFINITION_IDS = frozenset({"DEF_OR", "DEF_STRICT_IMP", "DEF_EQUIV_S"})
_SYSTEM_IDS = frozenset({"S1", "S2", "S3", "S4", "S5"})
_RULE_IDS = ("Sa", "Sb", "Ad", "Smp")

_EXPECTED_BASES = {
    "S1_B1_B7": ("S1", frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7"}), False),
    "S2_B1_B8": ("S2", frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"}), False),
    "S3_B1_B7_A8": ("S3", frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "A8"}), False),
    "S4_B1_B7_C10": ("S4", frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10"}), False),
    "S5_PRIMARY_B1_B7_C11": ("S5", frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C11"}), False),
    "S5_ALT_B1_B7_C10_C12": (
        "S5",
        frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10", "C12"}),
        True,
    ),
}

# These identify the independently certified lock objects, not certificate semantics.
_AST_LOCK_SHA256 = "90d44f404d2dec2407efc4a928777ebc2f080bd7049e1724da706980c39fad3a"
_CONTRACT_LOCK_SHA256 = "1ea5a56a2a1ecba85c8453cbd5f55af7eb15e32396f9157c85bc36e623939b25"
_CONTRACT_PATH = "spec/rules.yaml#canonical_certificate_contract"
_CONTRACT_VERSION = "1.1"


class _DuplicateYamlKeyError(yaml.YAMLError):
    pass


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise _DuplicateYamlKeyError(f"unhashable YAML mapping key at line {key_node.start_mark.line + 1}") from exc
        if duplicate:
            raise _DuplicateYamlKeyError(
                f"duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}"
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def _read_frozen_inputs(root: Path) -> dict[str, bytes]:
    """Read each manifest input once; validation and parsing share these bytes."""
    inputs = {}
    for relative_path in FROZEN_INPUT_SHA256:
        path = root / relative_path
        try:
            inputs[relative_path] = path.read_bytes()
        except OSError as exc:
            raise FrozenSpecFormatError(f"cannot read frozen YAML file {path}: {exc}") from exc
    return inputs


def _validate_baseline(inputs: Mapping[str, bytes]) -> None:
    for path, expected in FROZEN_INPUT_SHA256.items():
        actual = hashlib.sha256(inputs[path]).hexdigest()
        if actual != expected:
            raise FrozenSpecIntegrityError(
                f"frozen baseline SHA-256 mismatch: {path}; "
                f"expected {expected} from {ADMINISTRATIVE_FREEZE_COMMIT}, got {actual}"
            )


def _load_yaml_mapping(data: bytes, path: Path) -> Mapping[str, Any]:
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise FrozenSpecFormatError(f"cannot decode frozen YAML file {path}: {exc}") from exc
    try:
        value = yaml.load(text, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise FrozenSpecFormatError(f"invalid frozen YAML file {path}: {exc}") from exc
    if not isinstance(value, Mapping):
        raise FrozenSpecFormatError(f"frozen YAML top level must be a mapping: {path}")
    return value


def _canonical_json(value: Any) -> bytes:
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError) as exc:
        raise FrozenSpecFormatError(f"frozen object is not canonical-JSON serializable: {exc}") from exc
    return text.encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _require_mapping(value: Any, path: str, error_type: type[Exception] = FrozenSpecFormatError) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise error_type(f"{path} must be a mapping")
    return value


def _validate_component_metadata(documents: Mapping[str, Mapping[str, Any]]) -> None:
    for component, document in documents.items():
        if document.get("status") != FROZEN_STATUS:
            raise FrozenSpecStatusError(
                f"{component}.yaml status must be {FROZEN_STATUS!r}; got {document.get('status')!r}"
            )
        if str(document.get("spec_version")) != FROZEN_SPEC_VERSION:
            raise FrozenSpecVersionError(
                f"{component}.yaml spec_version must be {FROZEN_SPEC_VERSION!r}; "
                f"got {document.get('spec_version')!r}"
            )
        if document.get("component") != component or document.get("project") != PROJECT:
            raise FrozenSpecFormatError(f"{component}.yaml component/project identity mismatch")


def _validate_ast_lock(
    language: Mapping[str, Any], schemas_document: Mapping[str, Any], lock: Mapping[str, Any]
) -> None:
    if _digest(lock) != _AST_LOCK_SHA256:
        raise FrozenSpecFingerprintError("certified AST fingerprint lock object has changed")

    schemas = _require_mapping(schemas_document.get("schemas"), "schemas.schemas", FrozenSpecFingerprintError)
    definitions = _require_mapping(language.get("metadefinitions"), "language.metadefinitions", FrozenSpecFingerprintError)
    schema_hashes = _require_mapping(lock.get("schema_ast_sha256"), "schema_ast_sha256", FrozenSpecFingerprintError)
    definition_hashes = _require_mapping(
        lock.get("metadefinition_ast_sha256"), "metadefinition_ast_sha256", FrozenSpecFingerprintError
    )

    if frozenset(schemas) != _SCHEMA_IDS or frozenset(schema_hashes) != _SCHEMA_IDS:
        raise FrozenSpecFingerprintError("certified schema fingerprint domain mismatch")
    if frozenset(definitions) != _DEFINITION_IDS or frozenset(definition_hashes) != _DEFINITION_IDS:
        raise FrozenSpecFingerprintError("certified definition fingerprint domain mismatch")

    for schema_id in sorted(_SCHEMA_IDS):
        entry = _require_mapping(schemas[schema_id], f"schemas.{schema_id}", FrozenSpecFingerprintError)
        actual = _digest(entry.get("ast"))
        if schema_hashes.get(schema_id) != actual:
            raise FrozenSpecFingerprintError(f"certified schema AST fingerprint mismatch: {schema_id}")

    for definition_id in sorted(_DEFINITION_IDS):
        entry = _require_mapping(
            definitions[definition_id], f"metadefinitions.{definition_id}", FrozenSpecFingerprintError
        )
        actual = _digest({"lhs": entry.get("lhs"), "rhs": entry.get("rhs")})
        if definition_hashes.get(definition_id) != actual:
            raise FrozenSpecFingerprintError(f"certified definition AST fingerprint mismatch: {definition_id}")


def _validate_contract(rules: Mapping[str, Any], lock: Mapping[str, Any]) -> Mapping[str, Any]:
    if _digest(lock) != _CONTRACT_LOCK_SHA256:
        raise FrozenContractError("certificate-contract lock object has changed")
    if lock.get("contract_path") != _CONTRACT_PATH:
        raise FrozenContractError("certificate-contract lock path mismatch")
    if str(lock.get("contract_version")) != _CONTRACT_VERSION:
        raise FrozenContractError("certificate-contract lock version mismatch")

    contract = _require_mapping(
        rules.get("canonical_certificate_contract"),
        "rules.canonical_certificate_contract",
        FrozenContractError,
    )
    if str(contract.get("contract_version")) != _CONTRACT_VERSION:
        raise FrozenContractError("canonical certificate contract version mismatch")
    actual = _digest(contract)
    if lock.get("canonical_contract_sha256") != actual:
        raise FrozenContractError("canonical certificate contract fingerprint mismatch")
    return contract


def _basis_block(systems: Mapping[str, Any], system_id: str, alternative: bool) -> Mapping[str, Any]:
    system = _require_mapping(systems.get(system_id), f"systems.{system_id}", FrozenSpecBasisError)
    if system_id == "S5":
        key = "alternative_normalized_basis" if alternative else "primary_normalized_basis"
    else:
        if alternative:
            raise FrozenSpecBasisError(f"{system_id} has no alternative normalized basis")
        key = "normalized_basis"
    return _require_mapping(system.get(key), f"systems.{system_id}.{key}", FrozenSpecBasisError)


def _resolve_schemas(
    systems: Mapping[str, Any], system_id: str, alternative: bool = False, trail: tuple[str, ...] = ()
) -> frozenset[str]:
    marker = f"{system_id}:{alternative}"
    if marker in trail:
        raise FrozenSpecBasisError(f"basis inheritance cycle at {system_id}")
    block = _basis_block(systems, system_id, alternative)
    result: set[str] = set()
    parent = block.get("inherit_schemas_from")
    if parent is not None:
        if not isinstance(parent, str) or parent not in systems:
            raise FrozenSpecBasisError(f"invalid basis parent for {system_id}: {parent!r}")
        result.update(_resolve_schemas(systems, parent, False, trail + (marker,)))
    local = block.get("schemas")
    if local is None:
        local = block.get("add_schemas", [])
    if not isinstance(local, list) or any(not isinstance(item, str) for item in local):
        raise FrozenSpecBasisError(f"invalid schema list in {system_id} basis")
    if len(local) != len(set(local)):
        raise FrozenSpecBasisError(f"duplicate schema in {system_id} basis")
    result.update(local)
    return frozenset(result)


def _validate_bases(systems_document: Mapping[str, Any]) -> None:
    """Validate parsed input only; construct no trusted basis before integrity."""
    systems = _require_mapping(systems_document.get("systems"), "systems.systems", FrozenSpecBasisError)
    if frozenset(systems) != _SYSTEM_IDS:
        raise FrozenSpecBasisError("frozen system ID set mismatch")

    for expected_basis_id, (system_id, expected_schemas, alternative) in _EXPECTED_BASES.items():
        block = _basis_block(systems, system_id, alternative)
        actual_basis_id = block.get("basis_id")
        if actual_basis_id != expected_basis_id:
            raise FrozenSpecBasisError(
                f"{system_id} basis ID mismatch: expected {expected_basis_id!r}, got {actual_basis_id!r}"
            )
        resolved = _resolve_schemas(systems, system_id, alternative)
        if resolved != expected_schemas:
            raise FrozenSpecBasisError(f"{expected_basis_id} schema set mismatch")
        rules = block.get("rules")
        if rules != list(_RULE_IDS):
            raise FrozenSpecBasisError(f"{expected_basis_id} rule set/order mismatch")

    primary_id = "S5_PRIMARY_B1_B7_C11"
    alternative_id = "S5_ALT_B1_B7_C10_C12"
    if primary_id == alternative_id or _resolve_schemas(systems, "S5") == _resolve_schemas(systems, "S5", True):
        raise FrozenSpecBasisError("S5 primary and alternative bases must remain distinct")

    s5 = _require_mapping(systems["S5"], "systems.S5", FrozenSpecBasisError)
    policy = _require_mapping(s5.get("proof_basis_policy"), "systems.S5.proof_basis_policy", FrozenSpecBasisError)
    if policy.get("union_forbidden") is not True:
        raise FrozenSpecBasisError("S5 basis union must remain forbidden")
    if policy.get("allowed_basis_ids") != [primary_id, alternative_id]:
        raise FrozenSpecBasisError("S5 allowed basis ID list mismatch")

    certificate_policy = _require_mapping(
        systems_document.get("certificate_basis_policy"), "certificate_basis_policy", FrozenSpecBasisError
    )
    expected_ids = {
        "S1": ["S1_B1_B7"],
        "S2": ["S2_B1_B8"],
        "S3": ["S3_B1_B7_A8"],
        "S4": ["S4_B1_B7_C10"],
        "S5": [primary_id, alternative_id],
    }
    if certificate_policy.get("system_basis_ids") != expected_ids:
        raise FrozenSpecBasisError("certificate system/basis ID registry mismatch")


def _build_bases(systems_document: Mapping[str, Any]) -> Mapping[str, FrozenBasis]:
    """Construct trusted values only after all six input blobs authenticate."""
    systems = systems_document["systems"]
    return {
        basis_id: FrozenBasis(
            system_id=system_id,
            basis_id=basis_id,
            schemas=_resolve_schemas(systems, system_id, alternative),
            rules=tuple(_basis_block(systems, system_id, alternative)["rules"]),
            alternative=alternative,
        )
        for basis_id, (system_id, _, alternative) in _EXPECTED_BASES.items()
    }


def load_frozen_spec(repository_root: str | Path = ".") -> FrozenSpec:
    """Load, authenticate, and recursively freeze the M0 specification bundle.

    ``repository_root`` must contain the frozen ``spec`` and ``audit/m0``
    directories. Every validation failure raises a typed ``FrozenSpecError``
    subclass before any trusted structure is constructed. Existing semantic
    checks retain their specific diagnostics; complete raw-file integrity is
    an additional mandatory gate, not a replacement for those checks. Parsing
    and integrity checks use the same single-read byte snapshots. No Git or
    caller-supplied manifest is consulted at runtime.
    """

    root = Path(repository_root).resolve()
    inputs = _read_frozen_inputs(root)
    documents = {
        component: _load_yaml_mapping(inputs[f"spec/{component}.yaml"], root / "spec" / f"{component}.yaml")
        for component in _COMPONENTS
    }
    _validate_component_metadata(documents)

    ast_lock_path = "audit/m0/certified_ast_fingerprints.yaml"
    contract_lock_path = "audit/m0/certificate_contract_lock.yaml"
    ast_lock = _load_yaml_mapping(inputs[ast_lock_path], root / ast_lock_path)
    contract_lock = _load_yaml_mapping(inputs[contract_lock_path], root / contract_lock_path)
    _validate_ast_lock(documents["language"], documents["schemas"], ast_lock)
    _validate_contract(documents["rules"], contract_lock)
    _validate_bases(documents["systems"])
    _validate_baseline(inputs)

    bases = _build_bases(documents["systems"])

    frozen_language = deep_freeze(documents["language"])
    frozen_rules = deep_freeze(documents["rules"])
    frozen_schemas = deep_freeze(documents["schemas"])
    frozen_systems = deep_freeze(documents["systems"])

    return FrozenSpec(
        repository_root=root,
        spec_version=FROZEN_SPEC_VERSION,
        language=frozen_language,
        rules=frozen_rules,
        schemas=frozen_schemas,
        systems=frozen_systems,
        canonical_certificate_contract=frozen_rules["canonical_certificate_contract"],
        bases=deep_freeze(bases),
    )
