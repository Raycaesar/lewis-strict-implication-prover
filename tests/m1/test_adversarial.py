"""Mutate valid kernel fixtures and attack the complete production boundary.

Every rejection asserts the intended structured category, so an unrelated
failure (such as leftover unreachable nodes) cannot silently satisfy a test.
No M0 validator is used as the implementation oracle.
"""

import copy
import json

import pytest

from lewis_prover.errors import CertificateValidationError
from lewis_prover.kernel import check_certificate, instantiate_schema
from lewis_prover.syntax import Atom


KINDS = ("postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion")
P, Q, R = ({"op": "atom", "name": name} for name in ("p", "q", "r"))


def binary(op, left, right):
    return {"op": op, "left": copy.deepcopy(left), "right": copy.deepcopy(right)}


def conjunction(left, right):
    return binary("and", left, right)


def strict(left, right):
    return binary("strict_imp", left, right)


def expand_strict(value):
    return {"op": "neg", "arg": {"op": "poss", "arg": conjunction(
        value["left"], {"op": "neg", "arg": copy.deepcopy(value["right"])},
    )}}


def root(data):
    return data["nodes"][data["root"]]


def claim(data, formula):
    root(data)["conclusion"] = copy.deepcopy(formula)
    data["goal"] = copy.deepcopy(formula)


def rejects(data, frozen, code, *, node_id=None, detail=None):
    payload = json.dumps(data).encode("utf-8") if isinstance(data, dict) else data
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, frozen)
    error = caught.value
    assert error.code == code
    assert error.reason
    if node_id is not None:
        assert error.node_id == node_id
    if detail is not None:
        assert error.detail_code == detail
    return error


@pytest.mark.parametrize("kind", KINDS)
def test_positive_fixture_is_a_complete_proof_for_its_root_kind(m1_fixture_dir, m1_frozen, kind):
    checked = check_certificate((m1_fixture_dir / f"{kind}.json").read_bytes(), m1_frozen)
    certificate = checked.certificate
    assert certificate.nodes[certificate.root].justification.kind == kind
    assert certificate.nodes[certificate.root].conclusion == certificate.goal
    assert set(checked.node_order) == set(certificate.nodes)


@pytest.mark.parametrize("member,escaped", [("proof_id", False), ("kind", False), ("op", False),
                                           ("proof_id", True), ("kind", True), ("op", True), ("P", True)])
def test_recursive_and_escape_equivalent_duplicates(m1_document, m1_frozen, member, escaped):
    original = json.dumps(m1_document("postulate_instance"))
    alias = "\\u%04x%s" % (ord(member[0]), member[1:]) if escaped else member
    payload = original.replace(f'"{member}":', f'"{alias}": "shadow", "{member}":', 1)
    assert payload != original
    rejects(payload, m1_frozen, "document_decode_error", detail="DuplicateCertificateKeyError")


@pytest.mark.parametrize("payload,detail", [
    (b'\xff{}', "CertificateEncodingError"),
    (b'{"x":"\xc0\xaf"}', "CertificateEncodingError"),
    (b'{"x":"\xed\xa0\x80"}', "CertificateEncodingError"),
    (b'\xef\xbb\xbf{}', "CertificateEncodingError"),
    ('\ufeff{}', "CertificateEncodingError"),
    (b'{"x":"\\ud800"}', "CertificateStringError"),
    (b'{"\\udfff":"x"}', "CertificateStringError"),
    (b'{"x":NaN}', "NonstandardJsonConstantError"),
    (b'{"x":Infinity}', "NonstandardJsonConstantError"),
    (b'{"x":-Infinity}', "NonstandardJsonConstantError"),
    (b'{"x":1e99999}', "CertificateValueTypeError"),
    (b'{"x":-0}', "CertificateValueTypeError"),
    (b'{"x":true}', "CertificateValueTypeError"),
    (b'{"x":false}', "CertificateValueTypeError"),
    (b'{"x":null}', "CertificateValueTypeError"),
    (b'[]', "CertificateTopLevelTypeError"),
])
def test_document_profile_attacks(payload, detail, m1_frozen):
    rejects(payload, m1_frozen, "document_decode_error", detail=detail)


@pytest.mark.parametrize("location", ["proof", "node", "justification", "formula"])
def test_unknown_fields(m1_document, m1_frozen, location):
    data = m1_document("postulate_instance")
    target = {"proof": data, "node": root(data), "justification": root(data)["justification"],
              "formula": root(data)["conclusion"]["left"]}[location]
    target["hidden_rule"] = "necessitation"
    rejects(data, m1_frozen, "invalid_formula" if location == "formula" else "closed_world_field_error")


@pytest.mark.parametrize("bad", [
    {"op": "box", "arg": P}, {"op": "material_imp", "left": P, "right": Q},
    {"op": "=", "left": P, "right": Q}, {"meta": "P"},
    {"op": "neg"}, {"op": "poss", "arg": P, "right": Q},
    {"op": "and", "left": P}, {"op": "strict_imp", "left": P, "right": Q, "arg": R},
    {"op": "equiv_s", "arg": P}, {"op": "or", "left": P},
    {"op": "atom", "name": ""}, {"op": [], "arg": P},
])
def test_hidden_forbidden_constructors_and_malformed_arity(m1_document, m1_frozen, bad):
    data = m1_document("postulate_instance")
    claim(data, conjunction(P, bad))  # hide below an otherwise permitted constructor
    rejects(data, m1_frozen, "invalid_formula")


def test_expanded_postulate_is_not_its_surface_schema_instance(m1_document, m1_frozen):
    data = m1_document("postulate_instance")
    claim(data, expand_strict(root(data)["conclusion"]))
    rejects(data, m1_frozen, "invalid_postulate_instance", node_id="root", detail="CONCLUSION_MISMATCH")


@pytest.mark.parametrize("system,basis,schema_id", [
    ("S1", "S1_B1_B7", "B8"), ("S2", "S2_B1_B8", "A8"),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C11"),
    ("S5", "S5_PRIMARY_B1_B7_C11", "C10"), ("S5", "S5_PRIMARY_B1_B7_C11", "C12"),
])
def test_forbidden_primitive_admissions(m1_document, m1_frozen, system, basis, schema_id):
    data = m1_document("postulate_instance")
    env = {"P": Atom("p"), "Q": Atom("q")} if schema_id in ("A8", "B8") else {"P": Atom("p")}
    claim(data, instantiate_schema(schema_id, env, m1_frozen).to_ast())
    data.update(system=system, basis_id=basis)
    root(data)["justification"].update(schema_id=schema_id, schema_substitution={key: value.to_ast() for key, value in env.items()})
    rejects(data, m1_frozen, "invalid_postulate_instance", detail="SCHEMA_ADMISSION")


@pytest.mark.parametrize("basis", ["S5_UNION_B1_B7_C10_C11_C12", "S1_B1_B8", "S5_PRIMARY_B1_B7_C11+S5_ALT_B1_B7_C10_C12"])
def test_synthetic_union_basis(m1_document, m1_frozen, basis):
    data = m1_document("postulate_instance")
    data.update(system="S5", basis_id=basis)
    rejects(data, m1_frozen, "invalid_basis")


@pytest.mark.parametrize("env", [{}, {"P": P, "Q": Q}, {"p": P}])
def test_schema_map_domain_is_exact_and_namespaced(m1_document, m1_frozen, env):
    data = m1_document("postulate_instance")
    root(data)["justification"]["schema_substitution"] = env
    rejects(data, m1_frozen, "invalid_postulate_instance", detail="SCHEMA_INSTANTIATION")


@pytest.mark.parametrize("kind,field,key", [("postulate_instance", "schema_substitution", "P"), ("Sa", "atom_substitution", "p")])
def test_schema_metavariable_cannot_be_an_object_replacement(m1_document, m1_frozen, kind, field, key):
    data = m1_document(kind)
    root(data)["justification"][field][key] = {"meta": "Q"}
    rejects(data, m1_frozen, "invalid_formula")


def test_recursive_sa_trap(m1_document, m1_frozen):
    data = m1_document("Sa")
    # Source is B1(p,q), map is p -> q, q -> r. Recursion would give B1(r,r).
    claim(data, strict(conjunction(R, R), conjunction(R, R)))
    rejects(data, m1_frozen, "invalid_Sa", detail="CONCLUSION_MISMATCH")


@pytest.mark.parametrize("kind", ["Sb", "definition_conversion"])
@pytest.mark.parametrize("path", [["arg"], ["left", "left", "arg"], ["left", "name"], [["left"], ["right"]]])
def test_invalid_atom_name_and_multi_selection_paths(m1_document, m1_frozen, kind, path):
    data = m1_document(kind)
    root(data)["justification"]["occurrence_path"] = path
    rejects(data, m1_frozen, "invalid_" + kind)


def test_sb_cannot_replace_two_occurrences(m1_document, m1_frozen):
    data = m1_document("Sb")
    result = root(data)["conclusion"]
    result["right"]["left"] = copy.deepcopy(result["left"])
    data["goal"] = copy.deepcopy(result)
    rejects(data, m1_frozen, "invalid_Sb", detail="CONCLUSION_MISMATCH")


def test_inconsistent_definition_metavariables_from_accepted_parents(m1_document, m1_frozen):
    data = m1_document("Sb")
    # Both B1 instances remain valid, but they no longer have reverse sides.
    data["nodes"]["reverse"] = copy.deepcopy(data["nodes"]["forward"])
    forward = data["nodes"]["forward"]["conclusion"]
    data["nodes"]["mutual"]["conclusion"] = conjunction(forward, forward)
    rejects(data, m1_frozen, "invalid_definition_conversion", node_id="equivalence", detail="DEFINITION_CONVERSION")


def test_implicit_second_definition_conversion(m1_document, m1_frozen):
    data = m1_document("Sb")
    del data["nodes"]["target"]
    mutual = data["nodes"]["mutual"]["conclusion"]
    root(data)["justification"] = {"kind": "definition_conversion", "parents": ["equivalence"],
                                   "definition_id": "DEF_EQUIV_S", "direction": "expand", "occurrence_path": []}
    claim(data, conjunction(expand_strict(mutual["left"]), mutual["right"]))
    rejects(data, m1_frozen, "invalid_definition_conversion", node_id="root", detail="CONCLUSION_MISMATCH")


@pytest.mark.parametrize("kind", ["Sa", "Sb", "Ad", "Smp", "definition_conversion"])
@pytest.mark.parametrize("parents", [[], ["root", "root", "root"]])
def test_wrong_parent_arity(m1_document, m1_frozen, kind, parents):
    data = m1_document(kind)
    root(data)["justification"]["parents"] = parents
    rejects(data, m1_frozen, "invalid_" + kind)


@pytest.mark.parametrize("kind", ["Sb", "Ad", "Smp"])
def test_wrong_parent_order(m1_document, m1_frozen, kind):
    data = m1_document(kind)
    root(data)["justification"]["parents"].reverse()
    rejects(data, m1_frozen, "invalid_" + kind)


def test_sb_requires_literal_surface_equivalence(m1_document, m1_frozen):
    data = m1_document("Sb")
    root(data)["justification"]["parents"][0] = "mutual"
    del data["nodes"]["equivalence"]  # avoid an unrelated unreachable-node failure
    rejects(data, m1_frozen, "invalid_Sb", detail="SB_EQUIVALENCE_ROOT")


def test_ad_reversed_conclusion(m1_document, m1_frozen):
    data = m1_document("Ad")
    result = root(data)["conclusion"]
    claim(data, conjunction(result["right"], result["left"]))
    rejects(data, m1_frozen, "invalid_Ad", detail="CONCLUSION_MISMATCH")


def test_smp_antecedent_equality_only_after_expansion(m1_document, m1_frozen):
    data = m1_document("Smp")
    data["nodes"]["expanded"] = {
        "conclusion": expand_strict(data["nodes"]["antecedent"]["conclusion"]),
        "justification": {"kind": "definition_conversion", "parents": ["antecedent"],
                          "definition_id": "DEF_STRICT_IMP", "direction": "expand", "occurrence_path": []},
    }
    root(data)["justification"]["parents"][0] = "expanded"
    rejects(data, m1_frozen, "invalid_Smp", detail="SMP_ANTECEDENT")


@pytest.mark.parametrize("kind", ["necessitation", "material_MP", "modus_ponens", "S5_bridge"])
def test_hidden_modern_rules_or_bridge_macros(m1_document, m1_frozen, kind):
    data = m1_document("Sa")
    root(data)["justification"]["kind"] = kind
    rejects(data, m1_frozen, "invalid_structure")


@pytest.mark.parametrize("mutation,code", [
    ("missing_root", "missing_root"), ("missing_parent", "missing_parent"),
    ("empty_id", "invalid_identifier"), ("integer_parent", "document_decode_error"),
    ("text_coercion", "missing_parent"), ("cycle", "cycle"),
    ("garbage", "unreachable_node"), ("goal", "root_goal_mismatch"),
])
def test_dag_mutations(m1_document, m1_frozen, mutation, code):
    data = m1_document("Sa")
    if mutation == "missing_root":
        data["root"] = "absent"
    elif mutation == "missing_parent":
        del data["nodes"]["source"]
    elif mutation == "empty_id":
        data["nodes"][""] = data["nodes"].pop("source")
    elif mutation in ("integer_parent", "text_coercion"):
        data["nodes"]["1"] = data["nodes"].pop("source")
        root(data)["justification"]["parents"] = [1 if mutation == "integer_parent" else "01"]
    elif mutation == "cycle":
        data["nodes"]["source"]["justification"] = {"kind": "Sa", "parents": ["root"], "atom_substitution": {"q": P}}
    elif mutation == "garbage":
        data["nodes"]["unused"] = copy.deepcopy(data["nodes"]["source"])
    else:
        data["goal"] = P
    rejects(data, m1_frozen, code)
