def test_language_has_required_m0_ast(spec_bundle):
    formula_ast = spec_bundle.language["formula_ast"]
    assert {"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"} <= set(
        formula_ast
    )


def test_box_and_object_equality_are_not_ast_constructors(spec_bundle):
    formula_ast = spec_bundle.language["formula_ast"]
    assert "box" not in formula_ast
    assert "material_imp" not in formula_ast
    assert "object_equality" not in formula_ast


def test_plain_equality_is_metalanguage_only(spec_bundle):
    separation = spec_bundle.language["meta_object_separation"]
    assert separation["plain_equality"]["allowed_in_object_formula"] is False
    assert separation["definitional_equality"]["token"] == ":="
    assert separation["definitional_equality"]["level"] == "metalanguage"
    assert separation["definitional_equality"]["parse_as_formula"] is False


def test_equiv_s_is_object_language_node(spec_bundle):
    equiv = spec_bundle.language["formula_ast"]["equiv_s"]
    assert equiv["object_level"] is True
    assert equiv["primitive"] is False
    assert equiv["definition_id"] == "DEF_EQUIV_S"


def test_fishhook_surface_node_is_preserved(spec_bundle):
    strict_imp = spec_bundle.language["formula_ast"]["strict_imp"]
    operator = spec_bundle.language["operators"]["strict_imp"]
    assert strict_imp["first_class_surface_node"] is True
    assert operator["historical_name"] == "fishhook"
    assert spec_bundle.language["elaboration_policy"]["preserve_surface_fishhook"] is True


def test_box_sugar_is_disabled(spec_bundle):
    assert spec_bundle.language["elaboration_policy"]["permit_box_sugar"] is False
