"""Immutable values exposed by the frozen-spec loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


def deep_freeze(value: Any) -> Any:
    """Recursively copy YAML values into read-only Python containers."""

    if isinstance(value, Mapping):
        return MappingProxyType({key: deep_freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(deep_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class FrozenBasis:
    """One exact normalized basis admitted by the frozen M0 specification."""

    system_id: str
    basis_id: str
    schemas: frozenset[str]
    rules: tuple[str, ...]
    alternative: bool = False


@dataclass(frozen=True, slots=True)
class FrozenSpec:
    """Validated, deeply immutable view of the frozen M0 authorities."""

    repository_root: Path
    spec_version: str
    language: Mapping[str, Any]
    rules: Mapping[str, Any]
    schemas: Mapping[str, Any]
    systems: Mapping[str, Any]
    canonical_certificate_contract: Mapping[str, Any]
    bases: Mapping[str, FrozenBasis]
