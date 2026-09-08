"""Whole-certificate acceptance, with no search or renderer dependencies."""

from __future__ import annotations

from dataclasses import dataclass

from lewis_prover.errors import (
    CertificateBasisError, CertificateDocumentError, CertificateFieldError,
    CertificateFormulaError, CertificateIdentifierError, CertificateStructureError,
    CertificateValidationError, NodeCheckError,
)

from .certificate import load_certificate
from .certificate_model import PostulateInstance, ProofCertificate
from .checker import NodeChecker
from .model import FrozenSpec


@dataclass(frozen=True, slots=True)
class CheckedCertificate:
    """Immutable result of complete validation, including a topological order.

    Obtain this result from check_certificate, not by constructing an alleged
    success. It is output data, never an accepted input to the trusted API.
    Node IDs retain their original identities; there are no logical line numbers.
    """

    certificate: ProofCertificate
    node_order: tuple[str, ...]


def _parents(certificate: ProofCertificate) -> dict[str, tuple[str, ...]]:
    return {
        node_id: () if type(node.justification) is PostulateInstance else node.justification.parents
        for node_id, node in certificate.nodes.items()
    }


def _graph_order(certificate: ProofCertificate) -> tuple[str, ...]:
    """Validate the entire graph, then return deterministic DFS postorder.

    Traverse start IDs in code-point order and edges in declared parent order.
    An explicit stack avoids dependence on Python's recursion limit. Repeated
    parent references are legal edges, not duplicate certificate nodes.
    """
    nodes = certificate.nodes
    if certificate.root not in nodes:
        raise CertificateValidationError(
            "missing_root", "root does not resolve to a certificate node",
            node_id=certificate.root,
        )
    parents = _parents(certificate)
    for node_id in sorted(nodes):
        for index, parent in enumerate(parents[node_id]):
            if parent not in nodes:
                raise CertificateValidationError(
                    "missing_parent", f"parent {index} {parent!r} does not resolve",
                    node_id=node_id, kind=nodes[node_id].justification.kind,
                    related_ids=(parent,),
                )

    completed: set[str] = set()
    active: dict[str, int] = {}
    order: list[str] = []
    for start in sorted(nodes):
        if start in completed:
            continue
        active[start] = 0
        stack = [(start, iter(parents[start]))]
        while stack:
            node_id, edges = stack[-1]
            parent = next(edges, None)
            if parent is None:
                stack.pop()
                del active[node_id]
                completed.add(node_id)
                order.append(node_id)
            elif parent in active:
                cycle = tuple(entry[0] for entry in stack[active[parent]:]) + (parent,)
                raise CertificateValidationError(
                    "cycle", f"cyclic parent chain: {cycle!r}", node_id=node_id,
                    kind=nodes[node_id].justification.kind, related_ids=cycle,
                )
            elif parent not in completed:
                active[parent] = len(stack)
                stack.append((parent, iter(parents[parent])))

    reachable: set[str] = set()
    pending = [certificate.root]
    while pending:
        node_id = pending.pop()
        if node_id not in reachable:
            reachable.add(node_id)
            pending.extend(parents[node_id])
    unreachable = tuple(sorted(nodes.keys() - reachable))
    if unreachable:
        raise CertificateValidationError(
            "unreachable_node", f"nodes outside the root's dependency graph: {unreachable!r}",
            node_id=unreachable[0], related_ids=unreachable,
        )
    return tuple(order)


def check_certificate(data: bytes | bytearray | str, frozen_spec: FrozenSpec) -> CheckedCertificate:
    """Check canonical serialized JSON against a load_frozen_spec result.

    Mappings and model builders are deliberately not trusted-boundary inputs:
    they cannot establish that duplicate JSON names were rejected. The frozen
    loader's own typed errors remain separate from certificate validation.

    Error precedence is decode, closed structure (nodes in code-point order),
    root/reference resolution, cycles, reachability, logical nodes in stable
    topological order, then exact root/goal equality. Decode failures follow
    serialized order; graph/rule diagnostics do not depend on object order.
    """
    try:
        certificate = load_certificate(data, frozen_spec)
    except CertificateDocumentError as exc:
        raise CertificateValidationError(
            "document_decode_error", str(exc), detail_code=type(exc).__name__,
        ) from exc
    except CertificateStructureError as exc:
        if isinstance(exc, CertificateFieldError):
            code = "closed_world_field_error"
        elif isinstance(exc, CertificateFormulaError):
            code = "invalid_formula"
        elif isinstance(exc, CertificateBasisError):
            code = "invalid_basis"
        elif isinstance(exc, CertificateIdentifierError):
            code = "invalid_identifier"
        elif exc.kind is not None:
            code = "invalid_" + exc.kind
        else:
            code = "invalid_structure"
        raise CertificateValidationError(
            code, exc.reason, node_id=exc.node_id, kind=exc.kind,
            detail_code=type(exc).__name__,
        ) from exc

    order = _graph_order(certificate)
    checker = NodeChecker(certificate, frozen_spec)
    for node_id in order:
        try:
            checker.check_node(node_id)
        except NodeCheckError as exc:
            raise CertificateValidationError(
                "invalid_" + exc.kind, exc.reason, node_id=exc.node_id,
                kind=exc.kind, detail_code=exc.code,
            ) from exc
        except RecursionError as exc:
            raise CertificateValidationError(
                "validation_capacity_error", "formula operation exceeds traversal capacity",
                node_id=node_id, kind=certificate.nodes[node_id].justification.kind,
            ) from exc
    try:
        matches_goal = certificate.nodes[certificate.root].conclusion == certificate.goal
    except RecursionError as exc:
        raise CertificateValidationError(
            "validation_capacity_error", "root/goal comparison exceeds traversal capacity",
            node_id=certificate.root,
        ) from exc
    if not matches_goal:
        raise CertificateValidationError(
            "root_goal_mismatch", "root conclusion differs from the exact surface goal",
            node_id=certificate.root,
        )
    return CheckedCertificate(certificate, order)


def linearize(checked: CheckedCertificate) -> tuple[str, ...]:
    """Return the accepted DAG's stable parent-before-child node IDs, not lines."""
    if type(checked) is not CheckedCertificate:
        raise TypeError("linearize requires a CheckedCertificate result")
    return checked.node_order
