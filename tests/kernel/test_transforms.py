"""Structural regressions; none of these operations accepts a logical rule."""

from types import MappingProxyType

import pytest

from lewis_prover.errors import (
    AtomSubstitutionError, DefinitionConversionError, OccurrencePathError,
    SchemaInstantiationError, SchemaMatchError,
)
from lewis_prover.kernel import (
    DefinitionConversion, PostulateInstance, Sa, convert_definition,
    instantiate_schema, load_frozen_spec, match_schema, object_atom_names,
    replace_occurrence, resolve_occurrence, schema_metavariables, substitute_atoms,
)
from lewis_prover.syntax import (
    And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp,
    diagnostic_full_erasure, parse_formula,
)

P, Q, R = Atom("p"), Atom("q"), Atom("r")

# Independent surface expectations for all twelve registered schemas.
SCHEMAS = [
    ("B1", "PQ", "p ∧ q ⥽ q ∧ p"),
    ("B2", "PQ", "p ∧ q ⥽ p"),
    ("B3", "P", "p ⥽ p ∧ p"),
    ("B4", "PQR", "(p ∧ q) ∧ r ⥽ p ∧ (q ∧ r)"),
    ("B5", "P", "p ⥽ ∼∼p"),
    ("B6", "PQR", "(p ⥽ q) ∧ (q ⥽ r) ⥽ (p ⥽ r)"),
    ("B7", "PQ", "p ∧ (p ⥽ q) ⥽ q"),
    ("B8", "PQ", "◇(p ∧ q) ⥽ ◇p"),
    ("A8", "PQ", "(p ⥽ q) ⥽ (∼◇q ⥽ ∼◇p)"),
    ("C10", "P", "∼◇∼p ⥽ ∼◇∼∼◇∼p"),
    ("C11", "P", "◇p ⥽ ∼◇∼◇p"),
    ("C12", "P", "p ⥽ ∼◇∼◇p"),
]
DEFINITIONS = [
    ("DEF_OR", Or(P, Q), Neg(And(Neg(P), Neg(Q)))),
    ("DEF_STRICT_IMP", StrictImp(P, Q), Neg(Poss(And(P, Neg(Q))))),
    ("DEF_EQUIV_S", EquivS(P, Q), And(StrictImp(P, Q), StrictImp(Q, P))),
]
FORMULAS = [P, Neg(P), And(P, Q), Poss(P), Or(P, Q), StrictImp(P, Q), EquivS(P, Q)]


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


@pytest.mark.parametrize("schema_id,names,text", SCHEMAS)
def test_registered_schema_instantiation_and_matching(frozen, schema_id, names, text):
    substitution = {name: Atom(name.lower()) for name in names}
    expected = parse_formula(text)
    assert schema_metavariables(schema_id, frozen) == frozenset(names)
    assert instantiate_schema(schema_id, substitution, frozen) == expected
    environment = match_schema(schema_id, expected, frozen)
    assert environment == substitution
    with pytest.raises(TypeError):
        environment["P"] = R
    substitution.clear()
    assert environment["P"] == P


@pytest.mark.parametrize("schema_id,names,text", SCHEMAS)
def test_exact_schema_map_domain(frozen, schema_id, names, text):
    substitution = {name: Atom(name.lower()) for name in names}
    for missing in names:
        incomplete = {key: value for key, value in substitution.items() if key != missing}
        with pytest.raises(SchemaInstantiationError, match="missing"):
            instantiate_schema(schema_id, incomplete, frozen)
    with pytest.raises(SchemaInstantiationError, match="extra"):
        instantiate_schema(schema_id, {**substitution, "EXTRA": R}, frozen)


@pytest.mark.parametrize("schema_id", ["B9", "A7", "DEF_OR", "", None, 1, [], {}])
def test_only_registered_schema_ids(frozen, schema_id):
    with pytest.raises(SchemaInstantiationError):
        instantiate_schema(schema_id, {"P": P}, frozen)
    with pytest.raises(SchemaMatchError):
        match_schema(schema_id, P, frozen)


def test_schema_holes_and_object_atoms_are_disjoint_even_with_identical_names(frozen):
    # Replacements deliberately contain atom names equal to the OTHER map key.
    upper_p, upper_q = Atom("P"), Atom("Q")
    result = instantiate_schema("B1", {"P": upper_q, "Q": upper_p}, frozen)
    assert result == StrictImp(And(upper_q, upper_p), And(upper_p, upper_q))
    assert match_schema("B1", result, frozen) == {"P": upper_q, "Q": upper_p}
    with pytest.raises(SchemaInstantiationError):
        instantiate_schema("B1", {"p": P, "q": Q}, frozen)
    with pytest.raises(AtomSubstitutionError):
        substitute_atoms(And(P, Q), {"P": R}, frozen)


@pytest.mark.parametrize("replacement", [
    {"meta": "P"}, {"op": "atom", "name": "p"}, "p", None,
    Formula(), Neg(Formula()),
])
def test_substitution_values_must_be_object_formulas(frozen, replacement):
    with pytest.raises(SchemaInstantiationError):
        instantiate_schema("B3", {"P": replacement}, frozen)
    with pytest.raises(AtomSubstitutionError):
        substitute_atoms(P, {"p": replacement}, frozen)
    with pytest.raises(OccurrencePathError):
        replace_occurrence(P, [], replacement, frozen)
    with pytest.raises(SchemaMatchError):
        match_schema("B3", replacement, frozen)


@pytest.mark.parametrize("mapping", [[], "P=p", {Atom("P"): P}, {"": P}, {1: P}])
def test_invalid_substitution_maps_and_key_types(frozen, mapping):
    with pytest.raises(SchemaInstantiationError):
        instantiate_schema("B3", mapping, frozen)
    with pytest.raises(AtomSubstitutionError):
        substitute_atoms(P, mapping, frozen)


def test_schema_matching_uses_one_environment_for_every_repetition(frozen):
    inconsistent = StrictImp(And(P, Q), And(Q, R))
    with pytest.raises(SchemaMatchError, match="repeated"):
        match_schema("B1", inconsistent, frozen)
    expanded = diagnostic_full_erasure(Or(P, Q), frozen)
    formula = StrictImp(Or(P, Q), And(Or(P, Q), expanded))
    with pytest.raises(SchemaMatchError, match="repeated"):
        match_schema("B3", formula, frozen)


@pytest.mark.parametrize("replacement", FORMULAS)
def test_schema_instantiation_keeps_all_surface_constructors(frozen, replacement):
    result = instantiate_schema("B3", {"P": replacement}, frozen)
    assert result == StrictImp(replacement, And(replacement, replacement))
    assert result.left is replacement
    assert match_schema("B3", result, frozen)["P"] == replacement
    erased = diagnostic_full_erasure(result, frozen)
    with pytest.raises(SchemaMatchError):
        match_schema("B3", erased, frozen)


def test_classic_simultaneous_sa_trap(frozen):
    source = And(P, Q)
    substitution = {"p": Q, "q": R}
    result = substitute_atoms(source, substitution, frozen)
    assert result == And(Q, R)
    assert result != And(R, R)  # recursive/sequential p -> q -> r is forbidden
    assert source == And(P, Q) and substitution == {"p": Q, "q": R}
    assert substitute_atoms(source, {"q": R, "p": Q}, frozen) == result


def test_sa_swap_self_reference_and_identity_on_unmentioned_atoms(frozen):
    assert substitute_atoms(And(P, Q), {"p": Q, "q": P}, frozen) == And(Q, P)
    assert substitute_atoms(P, {"p": Neg(P)}, frozen) == Neg(P)
    replacement = And(P, Q)
    assert substitute_atoms(P, {"p": replacement}, frozen) is replacement
    result = substitute_atoms(And(P, R), {"p": Q}, frozen)
    assert result == And(Q, R) and result.right is R
    assert substitute_atoms(P, {"p": P}, frozen) == P  # nonempty identity map is legal


@pytest.mark.parametrize("mapping", [{}, {"missing": P}, {"p": P, "missing": Q}])
def test_sa_requires_nonempty_subset_of_source_atoms(frozen, mapping):
    with pytest.raises(AtomSubstitutionError, match="nonempty subset"):
        substitute_atoms(P, mapping, frozen)


@pytest.mark.parametrize("formula", FORMULAS)
def test_sa_walks_all_constructors_without_erasing_them(frozen, formula):
    assert object_atom_names(formula, frozen) == (frozenset({"p", "q"}) if hasattr(formula, "right") else frozenset({"p"}))
    result = substitute_atoms(formula, {"p": R}, frozen)
    if type(formula) is Atom:
        assert result == R
    elif type(formula) in (Neg, Poss):
        assert result == type(formula)(R)
    else:
        assert result == type(formula)(R, Q)


def test_object_atom_names_preserve_exact_string_identity(frozen):
    source = And(Atom("é"), Atom("e\u0301"))
    assert object_atom_names(source, frozen) == frozenset({"é", "e\u0301"})
    assert substitute_atoms(source, {"é": P}, frozen) == And(P, Atom("e\u0301"))


@pytest.mark.parametrize("formula", FORMULAS)
def test_occurrence_traversal_matches_the_single_frozen_registry(frozen, formula):
    assert resolve_occurrence(formula, [], frozen) is formula
    declaration = frozen.canonical_certificate_contract["occurrence_path"]
    fields = declaration["traversable_fields"][formula.op]
    for segment in declaration["legal_segments"]:
        if segment in fields:
            assert resolve_occurrence(formula, [segment], frozen) is getattr(formula, segment)
        else:
            with pytest.raises(OccurrencePathError):
                resolve_occurrence(formula, [segment], frozen)


@pytest.mark.parametrize("path", [
    "", "left", "left.right", None, 1, {}, {"left"}, [0], [True],
    ["name"], ["op"], ["*"], [""], [["left"], ["right"]], ["left", "*"],
])
def test_invalid_or_multiple_occurrence_paths(frozen, path):
    with pytest.raises(OccurrencePathError):
        resolve_occurrence(And(P, Q), path, frozen)
    with pytest.raises(OccurrencePathError):
        replace_occurrence(And(P, Q), path, R, frozen)


@pytest.mark.parametrize("path", [["name"], ["arg"], ["left"], ["right"], ["left", "arg"]])
def test_atom_has_no_traversable_child(frozen, path):
    with pytest.raises(OccurrencePathError):
        resolve_occurrence(P, path, frozen)


def test_paths_do_not_expand_definitions_or_visit_atom_names(frozen):
    assert resolve_occurrence(StrictImp(P, Q), ["left"], frozen) is P
    with pytest.raises(OccurrencePathError):
        resolve_occurrence(StrictImp(P, Q), ["arg"], frozen)
    with pytest.raises(OccurrencePathError):
        resolve_occurrence(And(P, Q), ["left", "name"], frozen)
    with pytest.raises(OccurrencePathError):
        resolve_occurrence(And(P, Q), ["left", "arg"], frozen)


def test_replacement_is_one_occurrence_even_when_subtrees_share_identity(frozen):
    shared = Or(P, Q)
    source = And(shared, shared)
    result = replace_occurrence(source, ["left", "left"], R, frozen)
    assert result == And(Or(R, Q), Or(P, Q))
    assert result != And(Or(R, Q), Or(R, Q))  # forbidden replace-all result
    assert result.right is shared and result.left.right is Q
    assert source.left is source.right is shared
    assert replace_occurrence(source, [], R, frozen) is R
    assert resolve_occurrence(source, ("right", "right"), frozen) is Q


@pytest.mark.parametrize("definition_id,surface,expanded", DEFINITIONS)
@pytest.mark.parametrize("path", [[], ["arg", "left"]])
def test_all_registered_definitions_expand_contract_at_exact_occurrence(frozen, definition_id, surface, expanded, path):
    wrap = (lambda value: Neg(And(value, R))) if path else (lambda value: value)
    assert convert_definition(wrap(surface), definition_id, "expand", path, frozen) == wrap(expanded)
    assert convert_definition(wrap(expanded), definition_id, "contract", path, frozen) == wrap(surface)
    assert surface != expanded


@pytest.mark.parametrize("definition_id", ["B1", "DEF_BOX", "DEF_OTHER", "", None, [], {}])
def test_only_registered_definitions(frozen, definition_id):
    with pytest.raises(DefinitionConversionError, match="unknown registered"):
        convert_definition(Or(P, Q), definition_id, "expand", [], frozen)


@pytest.mark.parametrize("direction", ["both", "left_to_right", "Expand", "expand,expand", [], None])
def test_definition_direction_is_exact(frozen, direction):
    with pytest.raises(DefinitionConversionError, match="direction"):
        convert_definition(Or(P, Q), "DEF_OR", direction, [], frozen)


@pytest.mark.parametrize("pattern", [
    And(StrictImp(P, Q), StrictImp(Q, R)),
    And(StrictImp(P, Q), StrictImp(R, P)),
    And(StrictImp(P, Q), StrictImp(P, Q)),
    And(StrictImp(Or(P, Q), R), StrictImp(R, Neg(And(Neg(P), Neg(Q))))),
])
def test_definition_contraction_rejects_inconsistent_repeated_metavariables(frozen, pattern):
    with pytest.raises(DefinitionConversionError, match="repeated"):
        convert_definition(pattern, "DEF_EQUIV_S", "contract", [], frozen)


def test_shared_environment_spans_matching_and_output(frozen):
    left, right = Or(P, Q), Poss(R)
    source = And(StrictImp(left, right), StrictImp(right, left))
    assert convert_definition(source, "DEF_EQUIV_S", "contract", [], frozen) == EquivS(left, right)
    assert convert_definition(EquivS(left, right), "DEF_EQUIV_S", "expand", [], frozen) == source


@pytest.mark.parametrize("path", [[], ["right"], ["left", "left"]])
def test_conversion_at_wrong_occurrence_rejects(frozen, path):
    source = And(Or(P, Q), P)
    with pytest.raises(DefinitionConversionError, match="does not match"):
        convert_definition(source, "DEF_OR", "expand", path, frozen)
    assert convert_definition(source, "DEF_OR", "expand", ["left"], frozen) == And(Neg(And(Neg(P), Neg(Q))), P)


def test_definition_conversion_cannot_replace_multiple_occurrences(frozen):
    shared = Or(P, Q)
    expansion = Neg(And(Neg(P), Neg(Q)))
    source = And(shared, shared)
    result = convert_definition(source, "DEF_OR", "expand", ["left"], frozen)
    assert result == And(expansion, shared)
    assert result != And(expansion, expansion)
    assert result.right is shared
    with pytest.raises(OccurrencePathError):
        convert_definition(source, "DEF_OR", "expand", [["left"], ["right"]], frozen)


def test_no_hidden_second_conversion_of_introduced_defined_nodes(frozen):
    source = EquivS(P, Q)
    once = convert_definition(source, "DEF_EQUIV_S", "expand", [], frozen)
    expected = And(StrictImp(P, Q), StrictImp(Q, P))
    second_result = And(Neg(Poss(And(P, Neg(Q)))), StrictImp(Q, P))
    assert once == expected
    assert once != second_result
    assert once != diagnostic_full_erasure(source, frozen)
    # A second conversion requires its own explicit operation and exact path.
    assert convert_definition(once, "DEF_STRICT_IMP", "expand", ["left"], frozen) == second_result
    with pytest.raises(DefinitionConversionError):
        convert_definition(second_result, "DEF_EQUIV_S", "contract", [], frozen)
    with pytest.raises(DefinitionConversionError):
        convert_definition(diagnostic_full_erasure(source, frozen), "DEF_EQUIV_S", "contract", [], frozen)


def test_nested_definition_in_a_replacement_is_never_converted_implicitly(frozen):
    source = Or(Or(P, Q), R)
    result = convert_definition(source, "DEF_OR", "expand", [], frozen)
    assert result == Neg(And(Neg(Or(P, Q)), Neg(R)))
    assert resolve_occurrence(result, ["arg", "left", "arg"], frozen) is source.left
    hidden_second = Neg(And(Neg(Neg(And(Neg(P), Neg(Q)))), Neg(R)))
    assert result != hidden_second


def test_transforms_consume_immutable_certificate_model_payloads(frozen):
    post = PostulateInstance("B3", MappingProxyType({"P": Or(P, Q)}))
    assert instantiate_schema(post.schema_id, post.schema_substitution, frozen) == StrictImp(Or(P, Q), And(Or(P, Q), Or(P, Q)))
    sa = Sa(("n1",), MappingProxyType({"p": Q, "q": R}))
    assert substitute_atoms(And(P, Q), sa.atom_substitution, frozen) == And(Q, R)
    conversion = DefinitionConversion(("n1",), "DEF_OR", "expand", ("left",))
    result = convert_definition(And(Or(P, Q), R), conversion.definition_id, conversion.direction, conversion.occurrence_path, frozen)
    assert result == And(Neg(And(Neg(P), Neg(Q))), R)
