"""Deterministic Unicode pretty-printer for exact surface formulas."""

from __future__ import annotations

from lewis_prover.errors import FormulaPrintError

from .formula import And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp

_PRECEDENCE = {
    Atom: 100,
    Neg: 90,
    Poss: 90,
    And: 70,
    Or: 60,
    StrictImp: 40,
    EquivS: 30,
}
_BINARY_SYMBOL = {And: "∧", Or: "∨", StrictImp: "⥽", EquivS: "≡ₛ"}
_RESERVED_ATOM_NAMES = frozenset({"strictif", "equiv_s"})


def _valid_atom_name(name: str) -> bool:
    if not name or name in _RESERVED_ATOM_NAMES:
        return False
    if not (name[0] == "_" or name[0].isalpha()):
        return False
    return all(char == "_" or char.isalnum() for char in name[1:])


def _needs_parentheses(child: Formula, parent: Formula, side: str) -> bool:
    child_precedence = _PRECEDENCE[type(child)]
    parent_precedence = _PRECEDENCE[type(parent)]
    if child_precedence != parent_precedence:
        return child_precedence < parent_precedence
    if isinstance(parent, (Neg, Poss)):
        return False
    if isinstance(parent, (And, Or)):
        return side == "right"
    if isinstance(parent, StrictImp):
        return side == "left"
    if isinstance(parent, EquivS):
        return True
    return False


def _render(formula: Formula, parent: Formula | None = None, side: str = "") -> str:
    if isinstance(formula, Atom):
        if not _valid_atom_name(formula.name):
            raise FormulaPrintError(f"atom name is not supported by human notation: {formula.name!r}")
        text = formula.name
    elif isinstance(formula, Neg):
        text = "∼" + _render(formula.arg, formula, "arg")
    elif isinstance(formula, Poss):
        text = "◇" + _render(formula.arg, formula, "arg")
    elif isinstance(formula, (And, Or, StrictImp, EquivS)):
        symbol = _BINARY_SYMBOL[type(formula)]
        text = f"{_render(formula.left, formula, 'left')} {symbol} {_render(formula.right, formula, 'right')}"
    else:
        raise FormulaPrintError(f"unsupported Formula subtype: {type(formula).__name__}")
    if parent is not None and _needs_parentheses(formula, parent, side):
        return f"({text})"
    return text


def pretty_formula(formula: Formula) -> str:
    """Render one parseable surface formula without definition erasure."""

    if not isinstance(formula, Formula):
        raise FormulaPrintError("pretty_formula requires an object Formula")
    return _render(formula)
