"""Explicit diagnostic-only expansion of registered frozen definitions."""

from __future__ import annotations

from typing import Any, Mapping

from lewis_prover.errors import FormulaErasureError
from lewis_prover.kernel.model import FrozenSpec

from .formula import And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp, formula_from_ast, formula_to_ast


def _match(pattern: Any, actual: Any, environment: dict[str, Any]) -> None:
    if isinstance(pattern, Mapping) and set(pattern) == {"meta"}:
        name = pattern["meta"]
        previous = environment.get(name)
        if previous is not None and previous != actual:
            raise FormulaErasureError(f"inconsistent repeated metavariable {name!r}")
        environment[name] = actual
        return
    if not isinstance(pattern, Mapping) or not isinstance(actual, Mapping) or set(pattern) != set(actual):
        raise FormulaErasureError("formula does not match registered definition LHS")
    for key in pattern:
        pattern_value = pattern[key]
        actual_value = actual[key]
        if isinstance(pattern_value, Mapping):
            _match(pattern_value, actual_value, environment)
        elif pattern_value != actual_value:
            raise FormulaErasureError("formula does not match registered definition LHS")


def _instantiate(template: Any, environment: Mapping[str, Any]) -> Any:
    if isinstance(template, Mapping):
        if set(template) == {"meta"}:
            name = template["meta"]
            if name not in environment:
                raise FormulaErasureError(f"unbound definition metavariable {name!r}")
            return environment[name]
        return {key: _instantiate(value, environment) for key, value in template.items()}
    if isinstance(template, (list, tuple)):
        return [_instantiate(value, environment) for value in template]
    return template


def _expand_root(formula: Formula, frozen_spec: FrozenSpec) -> Formula:
    operator = formula.op
    declaration = frozen_spec.language["formula_ast"].get(operator)
    if not isinstance(declaration, Mapping):
        raise FormulaErasureError(f"operator {operator!r} is absent from frozen formula_ast")
    definition_id = declaration.get("definition_id")
    if not isinstance(definition_id, str):
        raise FormulaErasureError(f"operator {operator!r} has no registered definition")
    definition = frozen_spec.language["metadefinitions"].get(definition_id)
    if not isinstance(definition, Mapping):
        raise FormulaErasureError(f"registered definition {definition_id!r} is unavailable")
    environment: dict[str, Any] = {}
    _match(definition["lhs"], formula_to_ast(formula), environment)
    return formula_from_ast(_instantiate(definition["rhs"], environment))


def diagnostic_full_erasure(formula: Formula, frozen_spec: FrozenSpec) -> Formula:
    """Recursively expand registered definitions to atom/neg/and/poss.

    This function is deliberately explicit and is not used by parsing,
    equality, hashing, substitution, or any rule-checking path.
    """

    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Neg):
        return Neg(diagnostic_full_erasure(formula.arg, frozen_spec))
    if isinstance(formula, Poss):
        return Poss(diagnostic_full_erasure(formula.arg, frozen_spec))
    if isinstance(formula, And):
        return And(
            diagnostic_full_erasure(formula.left, frozen_spec),
            diagnostic_full_erasure(formula.right, frozen_spec),
        )
    if isinstance(formula, (Or, StrictImp, EquivS)):
        return diagnostic_full_erasure(_expand_root(formula, frozen_spec), frozen_spec)
    raise FormulaErasureError(f"unsupported Formula subtype: {type(formula).__name__}")
