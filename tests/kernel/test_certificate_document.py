"""Production document-boundary tests, including the M0 conformance cases."""

import json

import pytest

from lewis_prover.errors import (
    CertificateDocumentError,
    CertificateEncodingError,
    CertificateStringError,
    CertificateTopLevelTypeError,
    CertificateValueTypeError,
    DuplicateCertificateKeyError,
    NonstandardJsonConstantError,
)
from lewis_prover.kernel import decode_certificate_document
from lewis_prover.kernel import document as production
from scripts.certificate_document_conformance import (
    CertificateDocumentError as M0DocumentError,
    load_certificate_json_text as m0_decode,
)


@pytest.mark.parametrize("text", [
    '{"root":"first","root":"second"}',
    '{"nodes":{"n":{"justification":{"kind":"Sa","kind":"Sb"}}}}',
    '{"goal":{"op":"atom","name":"p","name":"q"}}',
    '{"root":"first","r\\u006fot":"second"}',
    '{"nodes":{"n":{},"n":{}}}',
    '{"schema_substitution":{"P":{},"\\u0050":{}}}',
    '{"array":[{"deeper":[{"key":"x","key":"y"}]}]}',
    '{"😀":"one","\\ud83d\\ude00":"two"}',
    '{"x":"same","x":"same"}',
])
@pytest.mark.parametrize("as_bytes", [False, True])
def test_duplicates_reject_before_any_mapping_construction(text, as_bytes, monkeypatch):
    def materialization_must_not_start(value):
        pytest.fail("mapping construction began before full duplicate/profile validation")
    monkeypatch.setattr(production, "_materialize", materialization_must_not_start)
    with pytest.raises(DuplicateCertificateKeyError):
        decode_certificate_document(text.encode("utf-8") if as_bytes else text)


@pytest.mark.parametrize("data", [
    b'{"name":"\xff"}',
    b'{"name":"\xc0\xaf"}',  # overlong UTF-8
    b'{"name":"\xed\xa0\x80"}',  # encoded surrogate
    b'{"name":"\xf4\x90\x80\x80"}',  # beyond Unicode
    b'{"name":"\xe2\x82"}',  # truncated sequence
    b'\xef\xbb\xbf{}',
    '\ufeff{}',
])
def test_invalid_utf8_and_leading_bom(data):
    with pytest.raises(CertificateEncodingError):
        decode_certificate_document(data)


@pytest.mark.parametrize("text", [
    '{"name":"\\ud800"}',
    '{"name":"\\udfff"}',
    '{"\\ud800":"value"}',
    '{"array":["\\udc00"]}',
    '{"name":"\ud800"}',
    '{"name":"\ud83d\ude00"}',  # actual surrogates, not paired JSON escapes
])
def test_surrogates_in_values_and_member_names(text):
    with pytest.raises(CertificateStringError):
        decode_certificate_document(text)


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_nonstandard_constants(constant):
    with pytest.raises(NonstandardJsonConstantError):
        decode_certificate_document('{"x":[' + constant + ']}')


@pytest.mark.parametrize("scalar", [
    "0", "1", "-1", "-0", "0.0", "1.25", "1e10000", "-1e-10000",
    "true", "false", "null", "9" * 5000,
])
def test_forbidden_scalar_types_even_in_nested_arrays(scalar):
    with pytest.raises(CertificateValueTypeError):
        decode_certificate_document('{"outer":[{"inner":[' + scalar + ']}]}')


@pytest.mark.parametrize("text", ['[]', '[{}]', '"text"', 'true', 'false', 'null'])
def test_top_level_must_be_object(text):
    with pytest.raises(CertificateTopLevelTypeError):
        decode_certificate_document(text)


@pytest.mark.parametrize("text", [
    "", "root: n1", "{} {}", "{} trailing", "// comment\n{}", '{"x":"y",}',
    "{'x':'y'}", '{"x":"a\nb"}', '{"x":undefined}', '{"x":"\\x41"}',
    ' \ufeff{}',
])
def test_only_rfc8259_json_syntax(text):
    with pytest.raises(CertificateDocumentError):
        decode_certificate_document(text)


@pytest.mark.parametrize("data", [None, {}, [], 1, True])
def test_no_mapping_or_scalar_can_bypass_serialized_entry(data):
    with pytest.raises(CertificateDocumentError):
        decode_certificate_document(data)


def test_unicode_identity_and_permitted_string_values():
    text = '{"é":"composed","e\\u0301":"decomposed","A":"upper","a":"lower",' \
           '"01":"leading zero","1":"digit","":"",' \
           '"astral":"\\ud83d\\ude00","escaped control":"\\u0000",' \
           '"interior BOM":"\\ufeff","array":[{},[],"x"]}'
    decoded = decode_certificate_document(text)
    assert decoded["é"] == "composed"
    assert decoded["e\u0301"] == "decomposed"
    assert decoded["A"] != decoded["a"]
    assert decoded["01"] != decoded["1"]
    assert decoded[""] == ""
    assert decoded["astral"] == "😀"
    assert decoded["escaped control"] == "\x00"
    assert decoded["interior BOM"] == "\ufeff"
    assert decoded["array"] == [{}, [], "x"]
    assert decode_certificate_document(bytearray(text.encode("utf-8"))) == decoded


def test_empty_object_is_valid_document_without_being_a_certificate():
    assert decode_certificate_document(b" \r\n\t{} \r\n\t") == {}


@pytest.mark.parametrize("text", [
    '{}', '{"root":"n1","nodes":{}}',
    '{"root":"n1","root":"n2"}',
    '{"nested":{"kind":"Sa","kind":"Sb"}}',
    '{"formula":{"name":"p","name":"q"}}',
    '{"root":"a","r\\u006fot":"b"}',
    '{"name":"\\ud800"}', '{"name":"\\ud83d\\ude00"}',
    '{"x":NaN}', '{"x":Infinity}', '{"x":-Infinity}',
    '{"x":1}', '{"x":true}', '{"x":null}', '[]', '\ufeff{}',
    json.dumps({"é": "a", "e\u0301": "b"}),
])
def test_agrees_with_independent_m0_conformance_fixture(text):
    try:
        expected = m0_decode(text)
    except M0DocumentError:
        with pytest.raises(CertificateDocumentError):
            decode_certificate_document(text)
    else:
        assert decode_certificate_document(text) == expected
