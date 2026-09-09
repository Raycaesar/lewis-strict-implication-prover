"""Public API regressions for M1-CLOSE-01; no production authority is patched.

Only caller-owned data is changed. A frozen dataclass, mapping proxy, copied
field, or alleged provenance must never authorize non-M0 checking semantics.
"""

import json
import copy
import subprocess
import sys
from dataclasses import fields, replace
from types import MappingProxyType
from typing import Mapping

import pytest

from lewis_prover.errors import (
    CertificateValidationError, DefinitionConversionError, FrozenSpecIntegrityError,
    NodeCheckError, SchemaMatchError,
)
from lewis_prover import kernel
from lewis_prover.kernel import (
    FrozenBasis, FrozenSpec, NodeChecker, check_certificate, instantiate_schema,
    load_certificate, load_frozen_spec, schema_metavariables, validate_basis, validate_frozen_spec,
)
from lewis_prover.kernel.model import deep_freeze
from lewis_prover.syntax import And, Atom, EquivS, Neg, Or, Poss, StrictImp, diagnostic_full_erasure

OPS = ("atom", "neg", "and", "poss", "or", "strict_imp", "equiv_s")
KINDS = ("postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion")
ENTRIES = (
    "validate_frozen_spec", "check_certificate", "load_certificate", "certificate_from_document",
    "NodeChecker", "validate_basis", "schema_metavariables", "instantiate_schema", "match_schema",
    "object_atom_names", "substitute_atoms", "resolve_occurrence", "replace_occurrence",
    "convert_definition", "diagnostic_full_erasure",
)


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def thaw(value):
    if isinstance(value, Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [thaw(item) for item in value]
    if isinstance(value, frozenset):
        return set(value)
    if type(value) is FrozenBasis:
        return FrozenBasis(**{field.name: thaw(getattr(value, field.name)) for field in fields(FrozenBasis)})
    return value


def rebuilt(frozen, **changes):
    values = {field.name: getattr(frozen, field.name) for field in fields(FrozenSpec)}
    return FrozenSpec(**(values | changes))


def mutable_spec(frozen):
    return rebuilt(frozen, **{
        field.name: thaw(getattr(frozen, field.name))
        for field in fields(FrozenSpec) if field.name != "repository_root"
    })


def skipped_child_spec(frozen):
    language = thaw(frozen.language)
    language["formula_ast"]["and"]["fields"] = ["left"]
    return rebuilt(frozen, language=deep_freeze(language))


def two_node_invalid_conversion():
    # The B5 substitution is an arbitrary object formula. Contraction at its
    # left occurrence lacks the reverse implication required by DEF_EQUIV_S.
    p = Atom("p")
    forward = StrictImp(p, Neg(Neg(p)))
    repeated = And(forward, forward)
    parent = StrictImp(repeated, Neg(Neg(repeated)))
    claim = StrictImp(EquivS(p, Neg(Neg(p))), parent.right)
    return {
        "proof_id": "api-skipped-reverse", "system": "S1", "basis_id": "S1_B1_B7",
        "root": "root", "goal": claim.to_ast(), "nodes": {
            "post": {"conclusion": parent.to_ast(), "justification": {
                "kind": "postulate_instance", "schema_id": "B5",
                "schema_substitution": {"P": repeated.to_ast()},
            }},
            "root": {"conclusion": claim.to_ast(), "justification": {
                "kind": "definition_conversion", "parents": ["post"],
                "definition_id": "DEF_EQUIV_S", "direction": "contract",
                "occurrence_path": ["left"],
            }},
        },
    }


def postulate_document(frozen, schema_id, system="S1", basis_id="S1_B1_B7"):
    environment = {name: Atom(name.lower()) for name in schema_metavariables(schema_id, frozen)}
    formula = instantiate_schema(schema_id, environment, frozen)
    return {
        "proof_id": "api-primitive", "system": system, "basis_id": basis_id,
        "goal": formula.to_ast(), "root": "post", "nodes": {
            "post": {"conclusion": formula.to_ast(), "justification": {
                "kind": "postulate_instance", "schema_id": schema_id,
                "schema_substitution": {key: value.to_ast() for key, value in environment.items()},
            }},
        },
    }


@pytest.mark.parametrize("shape", ("two_node", "adjoined"))
def test_invalid_conversion_rejects_unverified_immutable_spec(frozen, repo_root, shape):
    document = two_node_invalid_conversion() if shape == "two_node" else json.loads(
        (repo_root / "tests/fixtures/m1/invalid/definition_conversion_skipped_reverse.json").read_bytes()
    )
    payload = json.dumps(document)
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, frozen)
    assert (caught.value.code, caught.value.detail_code, caught.value.node_id) == (
        "invalid_definition_conversion", "DEFINITION_CONVERSION", "root",
    )
    with pytest.raises(FrozenSpecIntegrityError):
        check_certificate(payload, skipped_child_spec(frozen))


def test_incremental_checker_rejects_unverified_spec_at_construction(frozen):
    certificate = load_certificate(json.dumps(two_node_invalid_conversion()), frozen)
    with pytest.raises(FrozenSpecIntegrityError):
        NodeChecker(certificate, skipped_child_spec(frozen))


def test_b8_in_s1_cannot_be_admitted_by_a_constructed_basis(frozen):
    basis = frozen.bases["S1_B1_B7"]
    invented = FrozenBasis(basis.system_id, basis.basis_id, basis.schemas | {"B8"}, basis.rules)
    forged = rebuilt(frozen, bases=MappingProxyType(dict(frozen.bases) | {basis.basis_id: invented}))
    payload = json.dumps(postulate_document(frozen, "B8"))
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, frozen)
    assert (caught.value.code, caught.value.detail_code) == ("invalid_postulate_instance", "SCHEMA_ADMISSION")
    with pytest.raises(FrozenSpecIntegrityError):
        check_certificate(payload, forged)
    with pytest.raises(FrozenSpecIntegrityError):
        validate_basis("S1", basis.basis_id, forged)


def test_incremental_session_cannot_change_through_retained_nested_alias(frozen):
    language = thaw(frozen.language)
    supplied = rebuilt(frozen, language=MappingProxyType(language))
    certificate = load_certificate(json.dumps(two_node_invalid_conversion()), frozen)
    checker = NodeChecker(certificate, supplied)
    checker.check_node("post")
    language["formula_ast"]["and"]["fields"][:] = ["left"]
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node("root")
    assert caught.value.code == "DEFINITION_CONVERSION"
    assert "root" not in checker.accepted_nodes


def exercise_entry(entry, spec, document, certificate):
    """Exercise supported APIs with valid inputs and check their real result."""
    p, q = Atom("p"), Atom("q")
    b3 = StrictImp(p, And(p, p))
    if entry == "validate_frozen_spec":
        assert validate_frozen_spec(spec).language["formula_ast"]["and"]["fields"] == ("left", "right")
    elif entry == "check_certificate":
        assert check_certificate(json.dumps(document), spec).certificate.goal == b3
    elif entry == "load_certificate":
        assert load_certificate(json.dumps(document), spec) == certificate
    elif entry == "certificate_from_document":
        assert kernel.certificate_from_document(document, spec) == certificate
    elif entry == "NodeChecker":
        assert NodeChecker(certificate, spec).check_node("post") == b3
    elif entry == "validate_basis":
        assert validate_basis("S1", "S1_B1_B7", spec).schemas == {f"B{i}" for i in range(1, 8)}
    elif entry == "schema_metavariables":
        assert schema_metavariables("B3", spec) == {"P"}
    elif entry == "instantiate_schema":
        assert instantiate_schema("B3", {"P": p}, spec) == b3
    elif entry == "match_schema":
        assert kernel.match_schema("B3", b3, spec) == {"P": p}
    elif entry == "object_atom_names":
        assert kernel.object_atom_names(Or(p, q), spec) == {"p", "q"}
    elif entry == "substitute_atoms":
        assert kernel.substitute_atoms(Or(p, q), {"p": q}, spec) == Or(q, q)
    elif entry == "resolve_occurrence":
        assert kernel.resolve_occurrence(Or(p, q), ["right"], spec) == q
    elif entry == "replace_occurrence":
        assert kernel.replace_occurrence(Or(p, q), ["right"], p, spec) == Or(p, p)
    elif entry == "convert_definition":
        assert kernel.convert_definition(Or(p, q), "DEF_OR", "expand", [], spec) == Neg(And(Neg(p), Neg(q)))
    else:
        assert entry == "diagnostic_full_erasure"
        assert diagnostic_full_erasure(StrictImp(p, q), spec) == Neg(Poss(And(p, Neg(q))))


def corrupt_spec(frozen, component):
    if component == "language":
        return skipped_child_spec(frozen)
    if component == "spec_version":
        return rebuilt(frozen, spec_version="0.7")
    data = thaw(getattr(frozen, component))
    if component == "rules":
        data["canonical_certificate_contract"]["closed_world"] = False
    elif component == "canonical_certificate_contract":
        data["occurrence_path"]["traversable_fields"]["and"] = ["left"]
    elif component == "schemas":
        data["schemas"]["B5"]["ast"] = {"meta": "P"}
    elif component == "systems":
        data["systems"]["S1"]["normalized_basis"]["schemas"].append("B8")
    else:
        assert component == "bases"
        data["S1_B1_B7"].schemas.add("B8")
    return rebuilt(frozen, **{component: data})


@pytest.mark.parametrize("entry", ENTRIES)
@pytest.mark.parametrize("component", (
    "language", "rules", "schemas", "systems", "canonical_certificate_contract", "bases", "spec_version",
))
def test_every_spec_using_public_api_authenticates_every_component(frozen, entry, component):
    document = postulate_document(frozen, "B3")
    certificate = load_certificate(json.dumps(document), frozen)
    with pytest.raises(FrozenSpecIntegrityError):
        exercise_entry(entry, corrupt_spec(frozen, component), document, certificate)


@pytest.mark.parametrize("entry", ENTRIES)
@pytest.mark.parametrize("representation", ("loader", "mutable_reconstruction"))
def test_all_supported_apis_preserve_genuine_m0_behavior(frozen, entry, representation):
    document = postulate_document(frozen, "B3")
    certificate = load_certificate(json.dumps(document), frozen)
    supplied = frozen if representation == "loader" else mutable_spec(frozen)
    exercise_entry(entry, supplied, document, certificate)


@pytest.mark.parametrize("op", OPS)
@pytest.mark.parametrize("field", ("arity", "fields", "primitive", "object_level", "constructor_domain"))
def test_complete_constructor_declarations_are_checked(frozen, op, field):
    language = thaw(frozen.language)
    declaration = language["formula_ast"][op]
    if field == "constructor_domain":
        del language["formula_ast"][op]
    elif field == "arity":
        declaration[field] += 1
    elif field == "fields":
        declaration[field] = []
    else:
        declaration[field] = not declaration[field]
    with pytest.raises(FrozenSpecIntegrityError, match="language.formula_ast"):
        validate_frozen_spec(rebuilt(frozen, language=language))


@pytest.mark.parametrize("op", ("and", "or", "strict_imp", "equiv_s"))
def test_constructor_field_order_cannot_change(frozen, op):
    language = thaw(frozen.language)
    language["formula_ast"][op]["fields"].reverse()
    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(rebuilt(frozen, language=language))


@pytest.mark.parametrize("op", ("or", "strict_imp", "equiv_s"))
@pytest.mark.parametrize("field", ("definition_id", "first_class_surface_node"))
def test_definition_linkage_and_surface_status_are_checked(frozen, op, field):
    language = thaw(frozen.language)
    language["formula_ast"][op][field] = "DEF_OTHER" if field == "definition_id" else False
    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(rebuilt(frozen, language=language))


@pytest.mark.parametrize("schema_id", [f"B{i}" for i in range(1, 9)] + ["A8", "C10", "C11", "C12"])
def test_every_primitive_schema_ast_is_checked(frozen, schema_id):
    schemas = thaw(frozen.schemas)
    schemas["schemas"][schema_id]["ast"] = {"meta": "P"}
    with pytest.raises(FrozenSpecIntegrityError, match=f"schemas.schemas.{schema_id}.ast"):
        validate_frozen_spec(rebuilt(frozen, schemas=schemas))


@pytest.mark.parametrize("definition_id", ("DEF_OR", "DEF_STRICT_IMP", "DEF_EQUIV_S"))
@pytest.mark.parametrize("side", ("lhs", "rhs"))
def test_every_definition_ast_side_is_checked(frozen, definition_id, side):
    language = thaw(frozen.language)
    language["metadefinitions"][definition_id][side] = {"meta": "P"}
    with pytest.raises(FrozenSpecIntegrityError, match=f"language.metadefinitions.{definition_id}.{side}"):
        validate_frozen_spec(rebuilt(frozen, language=language))


BASES = (
    ("S1", "S1_B1_B7", frozenset(f"B{i}" for i in range(1, 8))),
    ("S2", "S2_B1_B8", frozenset(f"B{i}" for i in range(1, 9))),
    ("S3", "S3_B1_B7_A8", frozenset(f"B{i}" for i in range(1, 8)) | {"A8"}),
    ("S4", "S4_B1_B7_C10", frozenset(f"B{i}" for i in range(1, 8)) | {"C10"}),
    ("S5", "S5_PRIMARY_B1_B7_C11", frozenset(f"B{i}" for i in range(1, 8)) | {"C11"}),
    ("S5", "S5_ALT_B1_B7_C10_C12", frozenset(f"B{i}" for i in range(1, 8)) | {"C10", "C12"}),
)


@pytest.mark.parametrize("system,basis_id,schemas", BASES)
@pytest.mark.parametrize("field", ("system_id", "basis_id", "schemas", "rules", "alternative"))
def test_every_derived_basis_field_is_authenticated(frozen, system, basis_id, schemas, field):
    basis = frozen.bases[basis_id]
    assert (basis.system_id, basis.schemas) == (system, schemas)
    replacement = {
        "system_id": "S6", "basis_id": "CALLER_BASIS", "schemas": basis.schemas | {"B9"},
        "rules": (*basis.rules, "CALLER_RULE"), "alternative": not basis.alternative,
    }[field]
    supplied = rebuilt(frozen, bases=dict(frozen.bases) | {basis_id: replace(basis, **{field: replacement})})
    with pytest.raises(FrozenSpecIntegrityError, match=f"bases.{basis_id}.{field}"):
        validate_basis(system, basis_id, supplied)


@pytest.mark.parametrize("change", ("extra", "missing", "union", "wrong_model", "wrong_key"))
def test_derived_basis_mapping_domain_and_models_cannot_be_forged(frozen, change):
    bases = dict(frozen.bases)
    if change == "extra":
        bases["S1_B1_B8"] = replace(bases["S1_B1_B7"], basis_id="S1_B1_B8")
    elif change == "missing":
        del bases["S2_B1_B8"]
    elif change == "union":
        primary, alternative = bases["S5_PRIMARY_B1_B7_C11"], bases["S5_ALT_B1_B7_C10_C12"]
        bases[primary.basis_id] = replace(primary, schemas=primary.schemas | alternative.schemas)
    elif change == "wrong_key":
        bases["S1_B1_B7"] = bases["S2_B1_B8"]
    else:
        bases["S1_B1_B7"] = {"system_id": "S1", "schemas": ["B8"]}
    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(rebuilt(frozen, bases=bases))


@pytest.mark.parametrize("system,basis_id,schema_id,admitted", (
    ("S1", "S1_B1_B7", "B8", False),
    ("S2", "S2_B1_B8", "A8", False),
    ("S2", "S2_B1_B8", "B8", True),
    ("S3", "S3_B1_B7_A8", "A8", True),
    ("S4", "S4_B1_B7_C10", "C10", True),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C11", False),
    ("S5", "S5_PRIMARY_B1_B7_C11", "C10", False),
    ("S5", "S5_PRIMARY_B1_B7_C11", "C12", False),
    ("S5", "S5_PRIMARY_B1_B7_C11", "C11", True),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C10", True),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C12", True),
))
def test_required_basis_admissions_in_whole_and_incremental_apis(frozen, system, basis_id, schema_id, admitted):
    supplied = mutable_spec(frozen)
    payload = json.dumps(postulate_document(frozen, schema_id, system, basis_id))
    certificate = load_certificate(payload, supplied)
    checker = NodeChecker(certificate, supplied)
    if admitted:
        assert check_certificate(payload, supplied).certificate == certificate
        assert checker.check_node("post") == certificate.goal
    else:
        with pytest.raises(CertificateValidationError) as caught:
            check_certificate(payload, supplied)
        assert caught.value.detail_code == "SCHEMA_ADMISSION"
        with pytest.raises(NodeCheckError) as node_error:
            checker.check_node("post")
        assert node_error.value.code == "SCHEMA_ADMISSION"


@pytest.mark.parametrize("component", (
    "language", "rules", "schemas", "systems", "canonical_certificate_contract", "bases",
))
def test_no_caller_owned_component_is_retained_after_validation(frozen, component):
    supplied = mutable_spec(frozen)
    alias = getattr(supplied, component)
    supplied = rebuilt(supplied, **{component: MappingProxyType(alias)})
    snapshot = validate_frozen_spec(supplied)
    assert snapshot is not supplied
    assert getattr(snapshot, component) is not alias
    payload = json.dumps(postulate_document(frozen, "B3"))
    certificate = load_certificate(payload, frozen)
    checker = NodeChecker(certificate, supplied)
    alias.clear()
    assert checker.check_node("post") == certificate.goal
    assert check_certificate(payload, snapshot).certificate == certificate
    with pytest.raises(FrozenSpecIntegrityError):
        check_certificate(payload, supplied)  # original object was never cached as trusted


def test_retained_mutable_basis_membership_cannot_affect_an_existing_session(frozen):
    bases = thaw(frozen.bases)
    caller_basis = bases["S1_B1_B7"]
    supplied = rebuilt(frozen, bases=MappingProxyType(bases))
    payload = json.dumps(postulate_document(frozen, "B8"))
    checker = NodeChecker(load_certificate(payload, frozen), supplied)
    admitted_basis = validate_basis("S1", "S1_B1_B7", supplied)
    assert admitted_basis is not caller_basis
    caller_basis.schemas.add("B8")
    caller_basis.rules.append("CALLER_RULE")
    assert "B8" not in admitted_basis.schemas
    assert admitted_basis.rules == ("Sa", "Sb", "Ad", "Smp")
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node("post")
    assert caught.value.code == "SCHEMA_ADMISSION"
    with pytest.raises(FrozenSpecIntegrityError):
        validate_basis("S1", "S1_B1_B7", supplied)


def test_validated_snapshot_is_recursively_immutable(frozen):
    snapshot = validate_frozen_spec(mutable_spec(frozen))

    def inspect(value):
        if type(value) in (FrozenSpec, FrozenBasis):
            for field in fields(value):
                if field.name != "repository_root":
                    inspect(getattr(value, field.name))
        elif isinstance(value, Mapping):
            assert type(value) is MappingProxyType
            assert all(type(key) is str for key in value)
            for item in value.values():
                inspect(item)
        elif type(value) in (tuple, frozenset):
            for item in value:
                inspect(item)
        else:
            assert type(value) in (str, int, bool, float, type(None))

    inspect(snapshot)
    with pytest.raises(TypeError):
        snapshot.language["formula_ast"]["and"]["fields"][0] = "right"
    with pytest.raises(TypeError):
        snapshot.language["metadefinitions"]["DEF_EQUIV_S"]["rhs"]["right"]["op"] = "atom"
    with pytest.raises(AttributeError):
        snapshot.bases["S1_B1_B7"].schemas.add("B8")
    with pytest.raises(AttributeError):
        snapshot.bases["S1_B1_B7"].rules += ("OTHER",)


@pytest.mark.parametrize("builder", (copy.copy, rebuilt, replace))
def test_reconstructed_and_copied_values_require_semantic_validation(frozen, builder):
    copied = builder(frozen)
    assert validate_frozen_spec(copied).language == frozen.language
    forged = replace(copied, language=skipped_child_spec(frozen).language)
    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(forged)


def test_fake_validation_and_provenance_markers_confer_no_trust(frozen):
    class ClaimedSpec(FrozenSpec):
        validated = True
        provenance = "load_frozen_spec"
        validation_marker = frozen
        canonical_contract_sha256 = "c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316"

    bad = skipped_child_spec(frozen)
    claimed = ClaimedSpec(**{field.name: getattr(bad, field.name) for field in fields(FrozenSpec)})
    with pytest.raises(FrozenSpecIntegrityError):
        check_certificate(json.dumps(two_node_invalid_conversion()), claimed)
    # Even the genuine root and version on an exact FrozenSpec do not help.
    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(bad)


@pytest.mark.parametrize("entry", ENTRIES)
def test_standalone_basis_is_never_a_trusted_spec(entry, frozen):
    document = postulate_document(frozen, "B3")
    certificate = load_certificate(json.dumps(document), frozen)
    with pytest.raises(FrozenSpecIntegrityError):
        exercise_entry(entry, frozen.bases["S1_B1_B7"], document, certificate)


def test_type_coercion_and_caller_equality_cannot_impersonate_authority(frozen):
    class EqualToAnything(str):
        def __eq__(self, other):
            return True

    for field, value in (("object_level", 1), ("arity", 2.0), ("fields", [EqualToAnything("bad"), "right"])):
        language = thaw(frozen.language)
        language["formula_ast"]["and"][field] = value
        with pytest.raises(FrozenSpecIntegrityError):
            validate_frozen_spec(rebuilt(frozen, language=language))


def test_mapping_equality_is_not_used_as_authentication(frozen):
    class LyingMapping(dict):
        def __eq__(self, other):
            return True

    with pytest.raises(FrozenSpecIntegrityError):
        validate_frozen_spec(rebuilt(frozen, language=LyingMapping(skipped_child_spec(frozen).language)))


@pytest.mark.parametrize("kind", KINDS)
def test_all_six_valid_kind_fixtures_pass_with_reconstructed_spec(frozen, repo_root, kind):
    supplied = mutable_spec(frozen)
    payload = (repo_root / f"tests/fixtures/m1/{kind}.json").read_bytes()
    checked = check_certificate(payload, supplied)
    checker = NodeChecker(load_certificate(payload, supplied), supplied)
    for node_id in checked.node_order:
        checker.check_node(node_id)
    assert checker.accepted_nodes[checked.certificate.root] == checked.certificate.goal


@pytest.mark.parametrize("definition_id,surface,expanded", (
    ("DEF_OR", Or(Atom("p"), Atom("q")), Neg(And(Neg(Atom("p")), Neg(Atom("q"))))),
    ("DEF_STRICT_IMP", StrictImp(Atom("p"), Atom("q")), Neg(Poss(And(Atom("p"), Neg(Atom("q")))))),
    ("DEF_EQUIV_S", EquivS(Atom("p"), Atom("q")), And(StrictImp(Atom("p"), Atom("q")), StrictImp(Atom("q"), Atom("p")))),
))
@pytest.mark.parametrize("direction", ("expand", "contract"))
@pytest.mark.parametrize("nested", (False, True))
def test_all_definition_directions_and_occurrences_preserve_exact_m0(frozen, definition_id, surface, expanded, direction, nested):
    source, expected = (surface, expanded) if direction == "expand" else (expanded, surface)
    path = []
    if nested:
        source, expected = And(Atom("r"), source), And(Atom("r"), expected)
        path = ["right"]
    assert kernel.convert_definition(source, definition_id, direction, path, mutable_spec(frozen)) == expected


def test_direct_match_and_definition_false_acceptances_remain_closed(frozen):
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    incorrect_b1 = StrictImp(And(p, q), And(q, r))
    forward = StrictImp(p, Neg(Neg(p)))
    with pytest.raises(SchemaMatchError):
        kernel.match_schema("B1", incorrect_b1, frozen)
    with pytest.raises(DefinitionConversionError):
        kernel.convert_definition(And(forward, forward), "DEF_EQUIV_S", "contract", [], frozen)
    for operation in (
        lambda spec: kernel.match_schema("B1", incorrect_b1, spec),
        lambda spec: kernel.convert_definition(And(forward, forward), "DEF_EQUIV_S", "contract", [], spec),
    ):
        with pytest.raises(FrozenSpecIntegrityError):
            operation(skipped_child_spec(frozen))


@pytest.mark.parametrize("corrupted", (False, True))
def test_direct_construction_as_first_process_call_authenticates_files(repo_root, corrupted):
    # A fresh interpreter has no loader-created object or cached authority.
    # Directly reconstruct all fields from ordinary YAML; the production API
    # must initialize its own reference through the authenticated file loader.
    script = """
import sys
from pathlib import Path
import yaml
from lewis_prover.kernel import FrozenSpec, FrozenBasis, validate_frozen_spec, instantiate_schema
from lewis_prover.errors import FrozenSpecIntegrityError
from lewis_prover.syntax import Atom, And, StrictImp
root = Path(sys.argv[1])
docs = {name: yaml.safe_load((root / 'spec' / (name + '.yaml')).read_bytes())
        for name in ('language', 'rules', 'schemas', 'systems')}
bases = {}
s1 = docs['systems']['systems']['S1']['normalized_basis']['schemas']
for system, entry in docs['systems']['systems'].items():
    for key, block in entry.items():
        if key.endswith('normalized_basis'):
            schemas = set(block.get('schemas', s1)) | set(block.get('add_schemas', []))
            bases[block['basis_id']] = FrozenBasis(system, block['basis_id'], schemas,
                block['rules'], key == 'alternative_normalized_basis')
bad = sys.argv[2] == 'True'
if bad:
    docs['language']['formula_ast']['and']['fields'] = ['left']
spec = FrozenSpec(root, '0.6', **docs,
    canonical_certificate_contract=docs['rules']['canonical_certificate_contract'], bases=bases)
try:
    result = validate_frozen_spec(spec)
except FrozenSpecIntegrityError:
    assert bad
else:
    assert not bad
    p = Atom('p')
    assert instantiate_schema('B3', {'P': p}, result) == StrictImp(p, And(p, p))
print('PASS')
"""
    run = subprocess.run([sys.executable, "-c", script, str(repo_root), str(corrupted)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout.strip() == "PASS"
