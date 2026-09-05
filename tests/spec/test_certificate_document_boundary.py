import copy

import pytest

from scripts.certificate_document_conformance import (
    CertificateDocumentError,
    DuplicateCertificateKeyError,
    NonstandardJsonConstantError,
    CertificateStringError,
    CertificateValueTypeError,
    load_certificate_json_bytes,
    load_certificate_json_text,
)
from scripts.validate_spec import validate_bundle


def _mutated_bundle(spec_bundle, rules):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        spec_bundle.language,
        rules,
        spec_bundle.schemas,
        spec_bundle.systems,
    )


def test_canonical_document_boundary_is_explicit(spec_bundle):
    boundary = spec_bundle.rules["canonical_certificate_contract"]["document_boundary"]
    assert boundary["canonical_serialized_format"] == "utf8_json_rfc8259_object"
    assert boundary["accepted_serialized_formats_at_kernel_boundary"] == [
        "utf8_json_rfc8259_object"
    ]
    assert boundary["duplicate_mapping_keys_policy"] == "reject_before_mapping_construction"
    assert boundary["duplicate_key_scope"] == "recursive_all_json_objects"
    assert boundary["parser_collapse_before_duplicate_detection"] == "forbidden"
    assert boundary["logical_validation_begins"] == "only_after_successful_strict_document_decode"


def test_mutation_duplicate_key_policy_to_last_wins_fails_freeze(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    boundary = rules["canonical_certificate_contract"]["document_boundary"]
    boundary["duplicate_mapping_keys_policy"] = "last_wins"
    boundary["parser_collapse_before_duplicate_detection"] = "permitted"

    issues = validate_bundle(_mutated_bundle(spec_bundle, rules), freeze=True)

    assert any(i.code == "CONTRACT_DOCUMENT_BOUNDARY" for i in issues)
    assert any(i.code == "FINGERPRINT_CONTRACT" for i in issues)


def test_duplicate_root_is_rejected_before_mapping_construction():
    text = '''
    {"proof_id":"p","system":"S1","basis_id":"S1_B1_B7",
     "goal":{"op":"atom","name":"p"},
     "root":"first","root":"second","nodes":{}}
    '''
    with pytest.raises(DuplicateCertificateKeyError):
        load_certificate_json_text(text)


def test_duplicate_nested_justification_kind_is_rejected_recursively():
    text = '''
    {
      "proof_id":"p",
      "system":"S1",
      "basis_id":"S1_B1_B7",
      "goal":{"op":"atom","name":"p"},
      "root":"n1",
      "nodes":{
        "n1":{
          "conclusion":{"op":"atom","name":"p"},
          "justification":{"kind":"Sa","kind":"Sb","parents":[]}
        }
      }
    }
    '''
    with pytest.raises(DuplicateCertificateKeyError):
        load_certificate_json_text(text)


def test_duplicate_nested_formula_field_is_rejected_recursively():
    text = '''
    {
      "proof_id":"p",
      "system":"S1",
      "basis_id":"S1_B1_B7",
      "goal":{"op":"atom","name":"p","name":"q"},
      "root":"n1",
      "nodes":{}
    }
    '''
    with pytest.raises(DuplicateCertificateKeyError):
        load_certificate_json_text(text)


def test_nonstandard_json_constants_are_rejected():
    with pytest.raises(NonstandardJsonConstantError):
        load_certificate_json_text('{"proof_id": NaN}')


def test_non_utf8_certificate_bytes_are_rejected():
    with pytest.raises(CertificateDocumentError):
        load_certificate_json_bytes(b'{"proof_id":"\xff"}')


def test_valid_canonical_json_document_decodes_to_object():
    obj = load_certificate_json_text(
        '{"proof_id":"p","system":"S1","basis_id":"S1_B1_B7",'
        '"goal":{"op":"atom","name":"p"},"root":"n1","nodes":{}}'
    )
    assert obj["proof_id"] == "p"
    assert obj["root"] == "n1"


def test_utf8_bom_is_rejected():
    with pytest.raises(CertificateDocumentError):
        load_certificate_json_bytes(b"\xef\xbb\xbf{}")


def test_unicode_surrogate_string_is_rejected():
    with pytest.raises(CertificateStringError):
        load_certificate_json_text('{"proof_id":"\\ud800"}')


def test_numbers_booleans_and_null_are_rejected_before_logical_validation():
    for text in ('{"proof_id":1}', '{"proof_id":true}', '{"proof_id":null}'):
        with pytest.raises(CertificateValueTypeError):
            load_certificate_json_text(text)

def test_duplicate_member_names_after_json_escape_decoding_are_rejected():
    # "r\\u006fot" decodes to exactly the same member name as "root".
    text = (
        '{"proof_id":"p","system":"S1","basis_id":"S1_B1_B7",'
        '"goal":{"op":"atom","name":"p"},'
        '"root":"first","r\\u006fot":"second","nodes":{}}'
    )
    with pytest.raises(DuplicateCertificateKeyError):
        load_certificate_json_text(text)
