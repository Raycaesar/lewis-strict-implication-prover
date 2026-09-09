"""Repeat the closure report's 69 file-mutation classes after the API repair.

Only temporary copies change. This matrix records the published mutation
classes; it does not depend on the independent audit's temporary artifacts.
"""

import shutil

import pytest
import yaml

from lewis_prover.errors import FrozenSpecError
from lewis_prover.kernel import load_frozen_spec
from lewis_prover.kernel.frozen_baseline import FROZEN_INPUT_SHA256

OPS = ("atom", "neg", "and", "poss", "or", "strict_imp", "equiv_s")


def mutation_cases():
    language, rules = "spec/language.yaml", "spec/rules.yaml"
    for op in OPS:
        for field, value in (("fields", ["unregistered_child"]), ("arity", 99),
                             ("primitive", "altered"), ("object_level", False)):
            yield language, ("formula_ast", op, field), value
    for op in ("and", "or", "strict_imp", "equiv_s"):
        yield language, ("formula_ast", op, "fields"), ["right", "left"]
    for op in ("or", "strict_imp", "equiv_s"):
        yield language, ("formula_ast", op, "definition_id"), "DEF_OTHER"
        yield language, ("formula_ast", op, "first_class_surface_node"), False
    contract = ("canonical_certificate_contract",)
    for op in OPS:
        yield rules, (*contract, "occurrence_path", "traversable_fields", op), ["name"]
    yield rules, (*contract, "occurrence_path", "legal_segments"), ["arg", "left", "right", "name"]
    yield rules, (*contract, "occurrence_path", "root"), ["left"]
    yield rules, (*contract, "occurrence_path", "definition_expansion_during_traversal"), "allowed"
    yield rules, (*contract, "kinds", "Sb", "root_replacement_allowed"), False
    yield "spec/schemas.yaml", ("schemas", "B5", "ast"), {"meta": "P"}
    yield language, ("metadefinitions", "DEF_EQUIV_S", "rhs"), {"meta": "P"}
    yield rules, (*contract, "closed_world"), False
    yield "audit/m0/certificate_contract_lock.yaml", ("canonical_contract_sha256",), "0" * 64
    yield "audit/m0/certified_ast_fingerprints.yaml", ("schema_ast_sha256", "B5"), "0" * 64
    yield "spec/systems.yaml", ("systems", "S1", "normalized_basis", "basis_id"), "S1_B1_B8"
    yield "spec/systems.yaml", ("systems", "S1", "normalized_basis", "schemas"), [f"B{i}" for i in range(1, 9)]
    yield "spec/systems.yaml", ("systems", "S5", "proof_basis_policy", "union_forbidden"), False
    yield language, ("operators", "and", "precedence"), 71
    yield language, ("operators", "strict_imp", "associativity"), "left"
    for component in ("language", "rules", "schemas", "systems"):
        yield f"spec/{component}.yaml", ("status",), "candidate_m0"
    for path in FROZEN_INPUT_SHA256:
        yield path, (), None


CASES = list(mutation_cases())
assert len(CASES) == 69


@pytest.mark.parametrize("relative,path,replacement", CASES, ids=[
    relative + "#" + (".".join(path) if path else "raw_bytes") for relative, path, _ in CASES
])
def test_all_69_published_file_mutation_classes_still_reject(tmp_path, repo_root, relative, path, replacement):
    for source in FROZEN_INPUT_SHA256:
        target = tmp_path / source
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / source, target)
    # Warm the in-process authority as well: it must not bypass later loads.
    load_frozen_spec(tmp_path)
    target = tmp_path / relative
    if path:
        document = yaml.safe_load(target.read_bytes())
        parent = document
        for segment in path[:-1]:
            parent = parent[segment]
        assert parent[path[-1]] != replacement
        parent[path[-1]] = replacement
        target.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        target.write_bytes(target.read_bytes() + b"\n# temporary file-integrity mutation\n")
    with pytest.raises(FrozenSpecError):
        load_frozen_spec(tmp_path)
