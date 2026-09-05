#!/usr/bin/env python3
"""M0 certificate-document decoding conformance fixture.

Normative machine authority:
    spec/rules.yaml#canonical_certificate_contract.document_boundary

M0.6 admits one serialized certificate format at the trusted boundary:
UTF-8 JSON (RFC 8259 syntax, project strict profile), with recursive duplicate
object-member names rejected before construction of the logical certificate
mapping.

This module is validation infrastructure, not the M1 trusted theorem checker.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CertificateDocumentError(ValueError):
    """Base error for canonical certificate-document decoding."""


class DuplicateCertificateKeyError(CertificateDocumentError):
    """Raised when a JSON object contains a duplicate member name."""


class NonstandardJsonConstantError(CertificateDocumentError):
    """Raised for lexical NaN/Infinity/-Infinity."""


class CertificateTopLevelTypeError(CertificateDocumentError):
    """Raised when the canonical document is not a JSON object."""


class CertificateStringError(CertificateDocumentError):
    """Raised when a decoded string contains a Unicode surrogate code point."""


class CertificateValueTypeError(CertificateDocumentError):
    """Raised when a decoded value uses a scalar type outside the M0 profile."""


def _reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateCertificateKeyError(
                f"duplicate JSON object member {key!r}"
            )
        result[key] = value
    return result


def _reject_constant(value: str):
    raise NonstandardJsonConstantError(
        f"nonstandard JSON constant {value!r} is forbidden"
    )


def _check_unicode_scalar_string(value: str, *, path: str) -> None:
    for ch in value:
        cp = ord(ch)
        if 0xD800 <= cp <= 0xDFFF:
            raise CertificateStringError(
                f"{path} contains forbidden Unicode surrogate U+{cp:04X}"
            )


def _validate_decoded_profile(value: Any, *, path: str = "$" ) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise CertificateValueTypeError(
                    f"{path} contains a non-string JSON object member name"
                )
            _check_unicode_scalar_string(key, path=f"{path}.<member-name>")
            _validate_decoded_profile(child, path=f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_decoded_profile(child, path=f"{path}[{index}]")
        return
    if isinstance(value, str):
        _check_unicode_scalar_string(value, path=path)
        return

    # The certificate data model uses only objects, arrays, and strings.
    # Reject bool before int because bool is an int subclass in Python.
    raise CertificateValueTypeError(
        f"{path} has forbidden decoded scalar type {type(value).__name__}"
    )


def load_certificate_json_text(text: str) -> dict[str, Any]:
    """Decode one canonical certificate JSON document.

    Duplicate names are detected recursively by ``object_pairs_hook`` before
    each JSON object is collapsed into a Python mapping.
    """
    if not isinstance(text, str):
        raise TypeError("certificate document text must be str")
    if text.startswith("\ufeff"):
        raise CertificateDocumentError("UTF-8 BOM is forbidden")

    try:
        obj = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except CertificateDocumentError:
        raise
    except json.JSONDecodeError as exc:
        raise CertificateDocumentError(str(exc)) from exc

    if not isinstance(obj, dict):
        raise CertificateTopLevelTypeError(
            "canonical certificate document must decode to one JSON object"
        )

    _validate_decoded_profile(obj)
    return obj


def load_certificate_json_bytes(data: bytes) -> dict[str, Any]:
    """Strict UTF-8 decoding followed by canonical JSON decoding."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("certificate document bytes must be bytes-like")
    raw = bytes(data)
    if raw.startswith(b"\xef\xbb\xbf"):
        raise CertificateDocumentError("UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise CertificateDocumentError(
            "certificate document is not strict UTF-8"
        ) from exc
    return load_certificate_json_text(text)


def load_certificate_json_file(path: str | Path) -> dict[str, Any]:
    return load_certificate_json_bytes(Path(path).read_bytes())


__all__ = [
    "CertificateDocumentError",
    "DuplicateCertificateKeyError",
    "NonstandardJsonConstantError",
    "CertificateTopLevelTypeError",
    "CertificateStringError",
    "CertificateValueTypeError",
    "load_certificate_json_text",
    "load_certificate_json_bytes",
    "load_certificate_json_file",
]
