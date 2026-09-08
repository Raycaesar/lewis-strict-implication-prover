"""Untrusted Lewis-style presentation of accepted surface proofs.

The kernel never imports this module. Line numbers and notation are display
artifacts; rendering cannot accept a certificate or supply logical evidence.
"""

from __future__ import annotations

import json

from lewis_prover.errors import FormulaPrintError
from lewis_prover.kernel import CheckedCertificate, linearize
from lewis_prover.syntax import pretty_formula


def _formula_text(formula) -> str:
    try:
        return pretty_formula(formula)
    except (FormulaPrintError, RecursionError):
        # The certificate language admits names beyond the small human parser.
        # Explicit surface JSON is a lossless fallback, not new input notation.
        return "AST " + json.dumps(formula.to_ast(), ensure_ascii=False, sort_keys=True)


def render_proof(checked: CheckedCertificate, *, first_line: int = 1) -> str:
    """Display exact surface formulas and ordered references for an accepted DAG.

    ``first_line`` affects presentation only. No erasure or logical rechecking
    happens here. Non-human-parser atom names use an explicit JSON AST fallback.
    """
    if type(checked) is not CheckedCertificate:
        raise TypeError("render_proof requires a CheckedCertificate result")
    if type(first_line) is not int or first_line < 1:
        raise ValueError("first_line must be a positive integer")
    certificate = checked.certificate
    order = linearize(checked)
    numbers = {node_id: number for number, node_id in enumerate(order, first_line)}
    lines = [f"{certificate.system} / {certificate.basis_id}  proof {json.dumps(certificate.proof_id, ensure_ascii=False)}"]
    for node_id in order:
        node = certificate.nodes[node_id]
        justification = node.justification
        kind = justification.kind
        references = ", ".join(str(numbers[parent]) for parent in getattr(justification, "parents", ()))
        if kind == "postulate_instance":
            label = justification.schema_id
            substitution = justification.schema_substitution
        elif kind == "definition_conversion":
            label = f"Df {justification.definition_id} {justification.direction} {references} @ {json.dumps(justification.occurrence_path)}"
            substitution = None
        else:
            label = f"{kind} {references}"
            substitution = justification.atom_substitution if kind == "Sa" else None
            if kind == "Sb":
                label += f" {justification.direction} @ {json.dumps(justification.occurrence_path)}"
        if substitution is not None:
            assignments = ", ".join(
                f"{json.dumps(key, ensure_ascii=False)} ↦ {_formula_text(value)}"
                for key, value in sorted(substitution.items())
            )
            label += f" {{{assignments}}}"
        identity = json.dumps(node_id, ensure_ascii=False)
        lines.append(f"{numbers[node_id]}. {_formula_text(node.conclusion)}    {label}  [id={identity}]")
    lines.append(f"Goal: {_formula_text(certificate.goal)}  (root line {numbers[certificate.root]})")
    return "\n".join(lines)
