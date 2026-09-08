"""Exact immutable objects for the seven frozen surface-AST constructors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping

from lewis_prover.errors import FormulaAstError


class Formula:
    """Marker base for object formulas; schema metavariables have no subtype."""

    __slots__ = ()

    def to_ast(self) -> dict[str, Any]:
        return formula_to_ast(self)


def _require_formula(value: Any, field: str) -> None:
    if not isinstance(value, Formula):
        raise FormulaAstError(f"{field} must be an object Formula")


@dataclass(frozen=True, slots=True)
class Atom(Formula):
    op: ClassVar[str] = "atom"
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise FormulaAstError("atom name must be a nonempty string")


@dataclass(frozen=True, slots=True)
class Neg(Formula):
    op: ClassVar[str] = "neg"
    arg: Formula

    def __post_init__(self) -> None:
        _require_formula(self.arg, "neg.arg")


@dataclass(frozen=True, slots=True)
class And(Formula):
    op: ClassVar[str] = "and"
    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _require_formula(self.left, "and.left")
        _require_formula(self.right, "and.right")


@dataclass(frozen=True, slots=True)
class Poss(Formula):
    op: ClassVar[str] = "poss"
    arg: Formula

    def __post_init__(self) -> None:
        _require_formula(self.arg, "poss.arg")


@dataclass(frozen=True, slots=True)
class Or(Formula):
    op: ClassVar[str] = "or"
    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _require_formula(self.left, "or.left")
        _require_formula(self.right, "or.right")


@dataclass(frozen=True, slots=True)
class StrictImp(Formula):
    op: ClassVar[str] = "strict_imp"
    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _require_formula(self.left, "strict_imp.left")
        _require_formula(self.right, "strict_imp.right")


@dataclass(frozen=True, slots=True)
class EquivS(Formula):
    op: ClassVar[str] = "equiv_s"
    left: Formula
    right: Formula

    def __post_init__(self) -> None:
        _require_formula(self.left, "equiv_s.left")
        _require_formula(self.right, "equiv_s.right")


_UNARY_TYPES = {"neg": Neg, "poss": Poss}
_BINARY_TYPES = {"and": And, "or": Or, "strict_imp": StrictImp, "equiv_s": EquivS}


def formula_to_ast(formula: Formula) -> dict[str, Any]:
    """Return the exact JSON-compatible surface AST without definition erasure."""

    _require_formula(formula, "formula")
    if isinstance(formula, Atom):
        return {"op": "atom", "name": formula.name}
    if isinstance(formula, (Neg, Poss)):
        return {"op": formula.op, "arg": formula_to_ast(formula.arg)}
    if isinstance(formula, (And, Or, StrictImp, EquivS)):
        return {
            "op": formula.op,
            "left": formula_to_ast(formula.left),
            "right": formula_to_ast(formula.right),
        }
    raise FormulaAstError(f"unsupported Formula subtype: {type(formula).__name__}")


def formula_from_ast(value: Any) -> Formula:
    """Decode one exact canonical object-formula AST.

    The accepted mapping shapes come directly from the seven constructors in
    frozen ``language.yaml``. A ``meta`` node is intentionally not an object
    formula and is rejected.
    """

    if not isinstance(value, Mapping):
        raise FormulaAstError("formula AST node must be a mapping")
    if "meta" in value:
        raise FormulaAstError("schema metavariables are forbidden in object formulas")

    op = value.get("op")
    if op == "atom":
        if set(value) != {"op", "name"}:
            raise FormulaAstError("atom requires exactly fields 'op' and 'name'")
        return Atom(value["name"])
    if op in _UNARY_TYPES:
        if set(value) != {"op", "arg"}:
            raise FormulaAstError(f"{op} requires exactly fields 'op' and 'arg'")
        return _UNARY_TYPES[op](formula_from_ast(value["arg"]))
    if op in _BINARY_TYPES:
        if set(value) != {"op", "left", "right"}:
            raise FormulaAstError(f"{op} requires exactly fields 'op', 'left', and 'right'")
        return _BINARY_TYPES[op](formula_from_ast(value["left"]), formula_from_ast(value["right"]))
    raise FormulaAstError(f"unknown or missing object-formula operator: {op!r}")
