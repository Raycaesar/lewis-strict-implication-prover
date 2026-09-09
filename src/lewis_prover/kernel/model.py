"""Specification data builders; construction alone does not establish trust.

The file loader creates recursively immutable values from authenticated YAML.
Caller construction may contain mutable descendants. Every trusted API uses
validate_frozen_spec and consumes only its owned immutable authority snapshot.
"""

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
    """Basis data, authenticated only through the owning spec's validation.

    No trusted checking API accepts a standalone caller-constructed basis.
    """

    system_id: str
    basis_id: str
    schemas: frozenset[str]
    rules: tuple[str, ...]
    alternative: bool = False


@dataclass(frozen=True, slots=True)
class FrozenSpec:
    """Specification data; this shallow frozen dataclass is not authentication.

    load_frozen_spec supplies immutable M0 data. Trusted consumers also check
    arbitrary constructed/reconstructed values through validate_frozen_spec.
    """

    repository_root: Path
    spec_version: str
    language: Mapping[str, Any]
    rules: Mapping[str, Any]
    schemas: Mapping[str, Any]
    systems: Mapping[str, Any]
    canonical_certificate_contract: Mapping[str, Any]
    bases: Mapping[str, FrozenBasis]
