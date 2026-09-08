from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from lewis_prover.errors import FormulaAstError, FormulaParseError
from lewis_prover.kernel import load_frozen_spec
from lewis_prover.syntax import (
    And,
    Atom,
    EquivS,
    Neg,
    Or,
    Poss,
    StrictImp,
    diagnostic_full_erasure,
    formula_from_ast,
    formula_to_ast,
    parse_formula,
    pretty_formula,
)

P = Atom("P")
Q = Atom("Q")
R = Atom("R")


@pytest.fixture(scope="module")
def frozen_spec(repo_root):
    return load_frozen_spec(repo_root)


@pytest.mark.parametrize(
    "formula",
    [
        P,
        Neg(P),
        And(P, Q),
        Poss(P),
        Or(P, Q),
        StrictImp(P, Q),
        EquivS(P, Q),
    ],
)
def test_all_seven_constructors_round_trip_canonical_ast(formula):
    assert formula_from_ast(formula_to_ast(formula)) == formula
    assert formula.to_ast() == formula_to_ast(formula)


def test_formulas_are_immutable_and_hash_structurally():
    formula = StrictImp(P, Or(Q, R))
    assert formula == StrictImp(Atom("P"), Or(Atom("Q"), Atom("R")))
    assert hash(formula) == hash(StrictImp(Atom("P"), Or(Atom("Q"), Atom("R"))))
    with pytest.raises(FrozenInstanceError):
        formula.left = Q


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("P ∨ Q ∧ R", Or(P, And(Q, R))),
        ("P ∧ Q ∧ R", And(And(P, Q), R)),
        ("P ∨ Q ∨ R", Or(Or(P, Q), R)),
        ("P ⥽ Q ⥽ R", StrictImp(P, StrictImp(Q, R))),
        ("P ∨ Q ⥽ R", StrictImp(Or(P, Q), R)),
        ("P ⥽ Q ≡ₛ R", EquivS(StrictImp(P, Q), R)),
        ("∼◇P ∧ Q", And(Neg(Poss(P)), Q)),
    ],
)
def test_frozen_precedence_and_associativity(text, expected):
    assert parse_formula(text) == expected


def test_strict_equivalence_is_non_associative():
    with pytest.raises(FormulaParseError, match="non-associative"):
        parse_formula("P ≡ₛ Q ≡ₛ R")
    assert parse_formula("(P ≡ₛ Q) ≡ₛ R") == EquivS(EquivS(P, Q), R)


@pytest.mark.parametrize(
    "formula",
    [
        Neg(Poss(And(P, Q))),
        And(P, And(Q, R)),
        Or(P, Or(Q, R)),
        StrictImp(StrictImp(P, Q), R),
        EquivS(P, EquivS(Q, R)),
        StrictImp(Or(P, Q), EquivS(Neg(P), Poss(R))),
    ],
)
def test_pretty_parse_round_trip_preserves_surface_ast(formula):
    assert parse_formula(pretty_formula(formula)) == formula


@pytest.mark.parametrize(
    ("formula", "expected"),
    [
        (And(And(P, Q), R), "P ∧ Q ∧ R"),
        (And(P, And(Q, R)), "P ∧ (Q ∧ R)"),
        (And(Or(P, Q), R), "(P ∨ Q) ∧ R"),
        (Or(And(P, Q), R), "P ∧ Q ∨ R"),
        (StrictImp(P, StrictImp(Q, R)), "P ⥽ Q ⥽ R"),
        (StrictImp(StrictImp(P, Q), R), "(P ⥽ Q) ⥽ R"),
        (EquivS(P, EquivS(Q, R)), "P ≡ₛ (Q ≡ₛ R)"),
        (Neg(And(P, Q)), "∼(P ∧ Q)"),
    ],
)
def test_pretty_printer_uses_exact_required_parentheses(formula, expected):
    assert pretty_formula(formula) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("~P", Neg(P)),
        ("¬P", Neg(P)),
        ("∼P", Neg(P)),
        ("<>P", Poss(P)),
        ("◇P", Poss(P)),
        ("P & Q", And(P, Q)),
        ("P ∧ Q", And(P, Q)),
        ("P · Q", And(P, Q)),
        ("P | Q", Or(P, Q)),
        ("P ∨ Q", Or(P, Q)),
        ("P strictif Q", StrictImp(P, Q)),
        ("P ⥽ Q", StrictImp(P, Q)),
        ("P equiv_s Q", EquivS(P, Q)),
        ("P ≡ₛ Q", EquivS(P, Q)),
        ("P <=> Q", EquivS(P, Q)),
    ],
)
def test_accepts_every_frozen_input_alias(text, expected):
    assert parse_formula(text) == expected


@pytest.mark.parametrize("text", ["P => Q", "P -> Q", "P → Q", "P = Q", "P := Q", "□P"])
def test_rejects_box_material_implication_and_object_equality(text):
    with pytest.raises(FormulaParseError):
        parse_formula(text)


@pytest.mark.parametrize(
    "ast",
    [
        {"meta": "P"},
        {"op": "atom"},
        {"op": "neg", "arg": {"op": "atom", "name": "P"}, "extra": "Q"},
        {"op": "and", "left": {"op": "atom", "name": "P"}},
        {"op": "and", "arg": {"op": "atom", "name": "P"}},
        {"op": "box", "arg": {"op": "atom", "name": "P"}},
        {"op": "material_imp", "left": {"op": "atom", "name": "P"}, "right": {"op": "atom", "name": "Q"}},
        {"op": "=", "left": {"op": "atom", "name": "P"}, "right": {"op": "atom", "name": "Q"}},
    ],
)
def test_rejects_schema_meta_forbidden_operators_and_malformed_arity(ast):
    with pytest.raises(FormulaAstError):
        formula_from_ast(ast)


def test_atoms_require_nonempty_names():
    with pytest.raises(FormulaAstError, match="nonempty"):
        Atom("")


def test_defined_surface_nodes_are_not_their_expansions(frozen_spec):
    strict = StrictImp(P, Q)
    strict_expansion = Neg(Poss(And(P, Neg(Q))))
    equivalence = EquivS(P, Q)

    assert strict != strict_expansion
    assert len({strict, strict_expansion}) == 2
    assert isinstance(parse_formula("P ⥽ Q"), StrictImp)
    assert isinstance(parse_formula("P ≡ₛ Q"), EquivS)
    assert diagnostic_full_erasure(strict, frozen_spec) == strict_expansion
    assert diagnostic_full_erasure(equivalence, frozen_spec) == diagnostic_full_erasure(
        And(StrictImp(P, Q), StrictImp(Q, P)), frozen_spec
    )


def test_diagnostic_erasure_uses_all_registered_definitions(frozen_spec):
    formula = Or(StrictImp(P, Q), EquivS(Q, R))
    erased = diagnostic_full_erasure(formula, frozen_spec)

    assert formula != erased
    assert {node["op"] for node in _walk_ast(formula_to_ast(erased))} <= {"atom", "neg", "and", "poss"}


def _walk_ast(node):
    yield node
    for field in ("arg", "left", "right"):
        child = node.get(field)
        if child is not None:
            yield from _walk_ast(child)
