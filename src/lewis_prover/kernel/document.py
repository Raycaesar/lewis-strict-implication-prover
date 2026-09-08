"""Production decoder for canonical_certificate_contract.document_boundary.

Implements the certified M0.6 strict UTF-8 JSON profile. This is only document
decoding: even an empty object is a valid document, not a checked certificate.
No YAML loader or M0 test fixture participates in this production boundary.
"""

from __future__ import annotations

import json
from typing import Any

from lewis_prover.errors import (
    CertificateDocumentError,
    CertificateEncodingError,
    CertificateStringError,
    CertificateTopLevelTypeError,
    CertificateValueTypeError,
    DuplicateCertificateKeyError,
    NonstandardJsonConstantError,
)


class _ObjectPairs(list):
    """Pair-preserving JSON object, distinct from a JSON array."""


def _scalar_string(value: str) -> None:
    if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
        raise CertificateStringError("decoded string contains a forbidden Unicode surrogate")


def _validate_value(value: Any) -> None:
    if isinstance(value, (dict, _ObjectPairs)):
        pairs = value.items() if isinstance(value, dict) else value
        names: set[str] = set()
        for key, child in pairs:
            if not isinstance(key, str):
                raise CertificateValueTypeError("object member names must be strings")
            _scalar_string(key)
            if key in names:
                raise DuplicateCertificateKeyError(f"duplicate JSON object member {key!r}")
            names.add(key)
            _validate_value(child)
    elif isinstance(value, list):
        for child in value:
            _validate_value(child)
    elif isinstance(value, str):
        _scalar_string(value)
    else:
        raise CertificateValueTypeError(
            f"forbidden decoded certificate value type: {type(value).__name__}"
        )


def validate_decoded_document(document: Any) -> None:
    """Check an in-memory decoded profile; cannot recover collapsed duplicates.

    Serialized input must always enter through ``decode_certificate_document``.
    This check also protects the separate structural factory from scalar/string
    policy bypass when it is called with a Python object directly.
    """
    if not isinstance(document, dict):
        raise CertificateTopLevelTypeError("canonical certificate document must be a JSON object")
    try:
        _validate_value(document)
    except RecursionError as exc:
        raise CertificateDocumentError("decoded document exceeds traversal capacity or is cyclic") from exc


def _reject_number(token: str) -> None:
    # Reject lexically without relying on int/float conversion, overflow, or
    # the host interpreter's integer-digit limit.
    raise CertificateValueTypeError("JSON numbers are forbidden in certificate documents")


def _reject_constant(token: str) -> None:
    raise NonstandardJsonConstantError(f"nonstandard JSON constant {token!r} is forbidden")


def _materialize(value: Any) -> Any:
    if isinstance(value, _ObjectPairs):
        return {key: _materialize(child) for key, child in value}
    if isinstance(value, list):
        return [_materialize(child) for child in value]
    return value


def decode_certificate_document(data: bytes | bytearray | str) -> dict[str, Any]:
    """Decode strict canonical UTF-8 JSON, rejecting ambiguity before mapping.

    All objects retain their member pairs until the complete decoded profile
    passes duplicate-name, Unicode-scalar, and value-type checks. Only then are
    mappings built. Name identity is Python string code-point equality: no
    trimming, Unicode normalization, case folding, or numeric coercion.
    """
    if isinstance(data, (bytes, bytearray)):
        try:
            text = bytes(data).decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise CertificateEncodingError("certificate document is not strict UTF-8") from exc
    elif isinstance(data, str):
        text = data
    else:
        raise CertificateDocumentError("certificate input must be UTF-8 bytes or text")
    if text.startswith("\ufeff"):
        raise CertificateEncodingError("leading UTF-8 BOM is forbidden")

    try:
        value = json.loads(
            text,
            strict=True,
            object_pairs_hook=_ObjectPairs,
            parse_int=_reject_number,
            parse_float=_reject_number,
            parse_constant=_reject_constant,
        )
        if not isinstance(value, _ObjectPairs):
            raise CertificateTopLevelTypeError("canonical certificate document must be a JSON object")
        _validate_value(value)
        return _materialize(value)
    except CertificateDocumentError:
        raise
    except (ValueError, RecursionError) as exc:
        raise CertificateDocumentError(f"cannot decode canonical certificate JSON: {exc}") from exc
