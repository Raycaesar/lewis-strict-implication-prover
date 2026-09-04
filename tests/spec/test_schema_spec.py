import copy

from scripts.validate_spec import EXPECTED_SCHEMA_IDS, validate_bundle


def test_schema_registry_exact(spec_bundle):
    assert set(spec_bundle.schemas["schemas"]) == set(EXPECTED_SCHEMA_IDS)


def test_a1_a7_and_b9_not_primitive(spec_bundle):
    ids = set(spec_bundle.schemas["schemas"])
    assert not ({f"A{i}" for i in range(1, 8)} & ids)
    assert "B9" not in ids


def test_every_schema_has_primary_provenance(spec_bundle):
    for sid, schema in spec_bundle.schemas["schemas"].items():
        source = schema["source"]
        assert source["work"] and source["edition"] and source["locus"], sid


def test_high_risk_c10_mutation_breaks_freeze_fingerprint(spec_bundle):
    schemas = copy.deepcopy(spec_bundle.schemas)
    c10 = schemas["schemas"]["C10"]["ast"]
    # Replace the whole audited AST with B1's AST: structurally valid but historically wrong.
    schemas["schemas"]["C10"]["ast"] = copy.deepcopy(schemas["schemas"]["B1"]["ast"])
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, spec_bundle.language, spec_bundle.rules, schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated, freeze=True)
    assert any(i.code == "FINGERPRINT_SCHEMA" for i in issues)
