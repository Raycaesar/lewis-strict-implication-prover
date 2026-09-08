"""Incremental node checking for all six frozen certificate kinds.

One session owns its accepted parents in one exact certificate basis. There
is no interface for seeding accepted nodes or importing them from another
session. A caller must explicitly check parents before children.

This incremental component does not check root/goal agreement, reachability,
or completion of the graph. Use dag.check_certificate for whole-proof checks.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from lewis_prover.errors import (
    CertificateBasisError, CertificateStructureError, NodeCheckError, StructuralTransformError,
)
from lewis_prover.syntax.formula import And, EquivS, Formula, StrictImp

from .basis import validate_basis
from .certificate_model import (
    Ad, DefinitionConversion, PostulateInstance, ProofCertificate, ProofNode, Sa, Sb, Smp,
)
from .model import FrozenSpec
from .transforms import (
    convert_definition, instantiate_schema, replace_occurrence, resolve_occurrence, substitute_atoms,
)


class NodeChecker:
    """Check individual nodes in a structurally loaded ``ProofCertificate``.

    ``frozen_spec`` must come from ``load_frozen_spec``. For serialized input,
    use ``load_certificate`` first. Direct data builders are rechecked for the
    node/formula/parent constraints required here; they confer no acceptance.
    Successful checks return exact surface conclusions and update only this
    session's private ledger. A failed check never adds a node to that ledger.
    """

    __slots__ = ("_certificate", "_spec", "_accepted")

    def __init__(self, certificate: ProofCertificate, frozen_spec: FrozenSpec):
        if type(certificate) is not ProofCertificate:
            raise CertificateStructureError("NodeChecker requires a structural ProofCertificate")
        self._certificate = certificate
        self._spec = frozen_spec
        self._accepted: dict[str, Formula] = {}

    @property
    def accepted_nodes(self) -> Mapping[str, Formula]:
        """Read-only view of this session's successfully checked conclusions."""
        return MappingProxyType(self._accepted)

    def check_node(self, node_id: str) -> Formula:
        """Accept one supported node only after exact surface validation."""
        if not isinstance(node_id, str) or not node_id:
            raise NodeCheckError(node_id, "<unknown>", "NODE_ID", "node ID must be a nonempty string")
        if node_id not in self._certificate.nodes:
            raise NodeCheckError(node_id, "<missing>", "NODE_MISSING", "node is absent from this certificate")
        node = self._certificate.nodes[node_id]
        if type(node) is not ProofNode:
            raise NodeCheckError(node_id, "<unknown>", "NODE_MODEL", "node must be a ProofNode")
        justification = node.justification
        kind = getattr(justification, "kind", "<unknown>")
        if not isinstance(kind, str):
            kind = "<unknown>"

        def fail(code: str, reason: str) -> None:
            raise NodeCheckError(node_id, kind, code, reason)

        if type(justification) not in (PostulateInstance, Sa, Sb, Ad, Smp, DefinitionConversion):
            fail("UNSUPPORTED_KIND", "justification model/kind is not implemented by this checker")
        declaration = self._spec.canonical_certificate_contract["kinds"][kind]

        basis_id = self._certificate.basis_id
        try:
            basis = validate_basis(self._certificate.system, basis_id, self._spec)
        except CertificateBasisError as exc:
            raise NodeCheckError(node_id, kind, "BASIS_IDENTITY", str(exc)) from exc

        try:
            # Root resolution validates the entire object formula and preserves
            # its exact surface tree; it performs no conversion or rewriting.
            resolve_occurrence(node.conclusion, (), self._spec)
        except StructuralTransformError as exc:
            raise NodeCheckError(node_id, kind, "CONCLUSION_FORMULA", str(exc)) from exc

        # postulate_instance has no parents field at all in the closed model.
        parents = () if type(justification) is PostulateInstance else justification.parents
        if not isinstance(parents, tuple) or len(parents) != declaration["parent_arity"]:
            fail("PARENT_ARITY", f"expected exactly {declaration['parent_arity']} ordered parent references")
        conclusions: list[Formula] = []
        for index, parent_id in enumerate(parents):
            if not isinstance(parent_id, str) or not parent_id:
                fail("PARENT_REFERENCE", f"parent {index} must be a nonempty string")
            if parent_id not in self._certificate.nodes:
                fail("PARENT_MISSING", f"parent {index} {parent_id!r} is absent from this certificate")
            if parent_id not in self._accepted:
                fail("PARENT_NOT_ACCEPTED", f"parent {index} {parent_id!r} has not been accepted in this session")
            conclusions.append(self._accepted[parent_id])

        if type(justification) is PostulateInstance:
            schema_id = justification.schema_id
            if not isinstance(schema_id, str) or schema_id not in basis.schemas:
                fail("SCHEMA_ADMISSION", f"schema {schema_id!r} is not primitive in exact basis {basis_id!r}")

        try:
            if type(justification) is PostulateInstance:
                operation = "SCHEMA_INSTANTIATION"
                expected = instantiate_schema(justification.schema_id, justification.schema_substitution, self._spec)
            elif type(justification) is Sa:
                operation = "ATOM_SUBSTITUTION"
                expected = substitute_atoms(conclusions[0], justification.atom_substitution, self._spec)
            elif type(justification) is Sb:
                operation = "SB_REPLACEMENT"
                equivalence, target = conclusions
                if type(equivalence) is not EquivS:
                    fail("SB_EQUIVALENCE_ROOT", "first parent must have literal surface equiv_s root")
                direction = justification.direction
                if not isinstance(direction, str) or direction not in declaration["direction_values"]:
                    fail("SB_DIRECTION", f"invalid Sb direction: {direction!r}")
                if direction == "left_to_right":
                    source_side, replacement = equivalence.left, equivalence.right
                else:
                    source_side, replacement = equivalence.right, equivalence.left
                path = justification.occurrence_path
                selected = resolve_occurrence(target, path, self._spec)
                if not path and declaration["root_replacement_allowed"] is not True:
                    fail("SB_ROOT_REPLACEMENT", "the frozen contract forbids root replacement")
                if selected != source_side:
                    fail("SB_SOURCE_MATCH", "selected target occurrence differs from the chosen surface equivalence side")
                expected = replace_occurrence(target, path, replacement, self._spec)
            elif type(justification) is Ad:
                operation = "ADJUNCTION"
                expected = And(conclusions[0], conclusions[1])
            elif type(justification) is Smp:
                operation = "STRICT_DETACHMENT"
                antecedent, implication = conclusions
                if type(implication) is not StrictImp:
                    fail("SMP_IMPLICATION_ROOT", "second parent must have literal surface strict_imp root")
                if antecedent != implication.left:
                    fail("SMP_ANTECEDENT", "first parent differs from the exact surface antecedent of the second parent")
                expected = implication.right
            else:
                operation = "DEFINITION_CONVERSION"
                expected = convert_definition(
                    conclusions[0], justification.definition_id, justification.direction,
                    justification.occurrence_path, self._spec,
                )
        except StructuralTransformError as exc:
            raise NodeCheckError(node_id, kind, operation, str(exc)) from exc

        if node.conclusion != expected:
            fail("CONCLUSION_MISMATCH", f"conclusion differs from exact surface result; expected {expected!r}, got {node.conclusion!r}")
        self._accepted[node_id] = node.conclusion
        return node.conclusion
