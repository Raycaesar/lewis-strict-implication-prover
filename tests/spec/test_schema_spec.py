EXPECTED = {
    "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A8", "C10", "C11", "C12"
}


def test_normalized_schema_registry_is_exact(spec_bundle):
    assert set(spec_bundle.schemas["schemas"]) == EXPECTED


def test_redundant_a_series_and_b9_are_not_primitive(spec_bundle):
    ids = set(spec_bundle.schemas["schemas"])
    assert not ({f"A{i}" for i in range(1, 8)} & ids)
    assert "B9" not in ids


def test_schema_policy_records_nonduplication(spec_bundle):
    assert spec_bundle.schemas["schema_policy"]["no_duplicate_A1_A7"] is True


def test_omitted_historical_schemas_are_documented(spec_bundle):
    omitted = spec_bundle.schemas["omitted_historical_schemas"]
    assert {"A1_A6", "A7", "B9"} <= set(omitted)


def test_every_primitive_schema_has_provenance(spec_bundle):
    for schema_id, schema in spec_bundle.schemas["schemas"].items():
        source = schema["source"]
        assert source["work"]
        assert source["edition"]
        assert source["locus"], schema_id


def test_every_schema_ast_starts_with_registered_operator(spec_bundle):
    registered = set(spec_bundle.language["formula_ast"])
    for schema_id, schema in spec_bundle.schemas["schemas"].items():
        assert schema["ast"]["op"] in registered, schema_id
