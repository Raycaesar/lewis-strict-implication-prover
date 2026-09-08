"""Closed structural loading from the frozen canonical certificate contract.

Successful loading is NOT proof acceptance. Reference resolution, DAG checks,
schema admission/substitution domains, rule matching, and root/goal equality
must be checked by the later logical checker. No formula is implicitly erased.
"""

from __future__ import annotations

from typing import Any, Mapping

from lewis_prover.errors import (
    CertificateFieldError,
    CertificateFormulaError,
    CertificateIdentifierError,
    CertificateStructureError,
    FormulaAstError,
)
from lewis_prover.syntax.formula import Formula, formula_from_ast

from .basis import validate_basis
from .certificate_model import (
    Ad, DefinitionConversion, Justification, PostulateInstance, ProofCertificate,
    ProofNode, Sa, Sb, Smp,
)
from .document import decode_certificate_document, validate_decoded_document
from .model import FrozenSpec


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CertificateStructureError(f"{path} must be an object")
    return value


def _fields(value: Any, declaration: Mapping[str, Any], path: str) -> dict[str, Any]:
    obj = _object(value, path)
    missing = set(declaration["required_fields"]) - obj.keys()
    unknown = obj.keys() - set(declaration["allowed_fields"])
    if missing or unknown:
        raise CertificateFieldError(f"{path}: missing fields {sorted(missing)}, unknown fields {sorted(unknown)}")
    return obj


def _identifier(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise CertificateIdentifierError(f"{path} must be a nonempty string")
    return value


def _formula(value: Any, path: str) -> Formula:
    # Check the discriminator before delegating, including unhashable JSON
    # containers that the original standalone formula decoder cannot look up.
    if not isinstance(value, dict) or not isinstance(value.get("op"), str):
        raise CertificateFormulaError(f"{path} must be an object-formula AST with a string op")
    try:
        return formula_from_ast(value)
    except (FormulaAstError, TypeError, RecursionError) as exc:
        raise CertificateFormulaError(f"{path}: malformed object-formula AST: {exc}") from exc


def _substitution(value: Any, path: str) -> dict[str, Formula]:
    return {
        _identifier(name, f"{path}.<key>"): _formula(formula, f"{path}[{name!r}]")
        for name, formula in sorted(_object(value, path).items())
    }


def _justification(value: Any, contract: Mapping[str, Any], path: str) -> Justification:
    obj = _object(value, path)
    kind = obj.get("kind")
    if not isinstance(kind, str) or kind not in contract["kinds"]:
        raise CertificateStructureError(f"{path}: unknown justification kind {kind!r}")
    if kind not in {model.kind for model in (PostulateInstance, Sa, Sb, Ad, Smp, DefinitionConversion)}:
        raise CertificateStructureError(f"{path}: unsupported justification model {kind!r}")
    declaration = contract["kinds"][kind]
    obj = _fields(obj, declaration, path)

    if kind == "postulate_instance":
        return PostulateInstance(
            _identifier(obj["schema_id"], f"{path}.schema_id"),
            _substitution(obj["schema_substitution"], f"{path}.schema_substitution"),
        )

    parents = obj["parents"]
    if not isinstance(parents, list) or len(parents) != declaration["parent_arity"]:
        raise CertificateStructureError(f"{path}.parents must be an array of length {declaration['parent_arity']}")
    parents = tuple(_identifier(parent, f"{path}.parents[{i}]") for i, parent in enumerate(parents))
    if kind == "Sa":
        substitution = _substitution(obj["atom_substitution"], f"{path}.atom_substitution")
        if not substitution:
            raise CertificateStructureError(f"{path}.atom_substitution must be nonempty")
        return Sa(parents, substitution)
    if kind == "Ad":
        return Ad(parents)
    if kind == "Smp":
        return Smp(parents)

    direction = obj["direction"]
    if not isinstance(direction, str) or direction not in declaration["direction_values"]:
        raise CertificateStructureError(f"{path}.direction is not allowed for {kind}")
    occurrence_path = obj["occurrence_path"]
    segments = contract["occurrence_path"]["legal_segments"]
    if not isinstance(occurrence_path, list) or any(
        not isinstance(segment, str) or segment not in segments for segment in occurrence_path
    ):
        raise CertificateStructureError(f"{path}.occurrence_path must be an array of legal path segments")
    if kind == "Sb":
        return Sb(parents, direction, tuple(occurrence_path))
    return DefinitionConversion(
        parents, _identifier(obj["definition_id"], f"{path}.definition_id"), direction, tuple(occurrence_path)
    )


def certificate_from_document(document: dict[str, Any], frozen_spec: FrozenSpec) -> ProofCertificate:
    """Build immutable structural data; do not treat a mapping as serialized input.

    This factory cannot discover duplicates discarded by an earlier decoder.
    Call ``load_certificate`` at the trusted bytes/text boundary. Successful
    structure loading leaves all graph/theorem obligations for the checker.
    """
    validate_decoded_document(document)
    contract = frozen_spec.canonical_certificate_contract
    proof = _fields(document, contract["top_level"], "proof")
    proof_id = _identifier(proof["proof_id"], "proof.proof_id")
    system = proof["system"]
    basis_id = proof["basis_id"]
    validate_basis(system, basis_id, frozen_spec)
    root = _identifier(proof["root"], "proof.root")
    goal = _formula(proof["goal"], "proof.goal")
    nodes: dict[str, ProofNode] = {}
    for node_id, value in sorted(_object(proof["nodes"], "proof.nodes").items()):
        node_id = _identifier(node_id, "proof.nodes.<key>")
        path = f"proof.nodes[{node_id!r}]"
        try:
            node = _fields(value, contract["node"], path)
            nodes[node_id] = ProofNode(
                _formula(node["conclusion"], f"{path}.conclusion"),
                _justification(node["justification"], contract, f"{path}.justification"),
            )
        except CertificateStructureError as exc:
            exc.node_id = node_id
            justification = value.get("justification") if isinstance(value, dict) else None
            kind = justification.get("kind") if isinstance(justification, dict) else None
            exc.kind = kind if isinstance(kind, str) and kind in contract["kinds"] else None
            raise
    # Validation order determines diagnostics, not the exposed mapping order.
    # Preserve the structural loader's original input-order presentation API.
    ordered_nodes = {node_id: nodes[node_id] for node_id in proof["nodes"]}
    return ProofCertificate(proof_id, system, basis_id, goal, root, ordered_nodes)


def load_certificate(data: bytes | bytearray | str, frozen_spec: FrozenSpec) -> ProofCertificate:
    """Trusted entry point: strict document decode, then structural loading.

    The spec must come from ``load_frozen_spec``. This function does not prove
    theorem validity and does not resolve or accept proof steps.
    """
    document = decode_certificate_document(data)
    return certificate_from_document(document, frozen_spec)
