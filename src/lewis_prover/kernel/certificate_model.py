"""Immutable structural certificate values, not evidence of theorem validity.

Use ``load_certificate`` for serialized input or ``certificate_from_document``
for already decoded documents. Direct constructors are ordinary data builders;
field/type validation against the frozen contract belongs to those factories.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import ClassVar, Mapping, TypeAlias

from lewis_prover.syntax.formula import Formula


@dataclass(frozen=True, slots=True)
class PostulateInstance:
    kind: ClassVar[str] = "postulate_instance"
    schema_id: str
    schema_substitution: Mapping[str, Formula]

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_substitution", MappingProxyType(dict(self.schema_substitution)))


@dataclass(frozen=True, slots=True)
class _ParentJustification:
    parents: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "parents", tuple(self.parents))


@dataclass(frozen=True, slots=True)
class Sa(_ParentJustification):
    kind: ClassVar[str] = "Sa"
    atom_substitution: Mapping[str, Formula]

    def __post_init__(self) -> None:
        _ParentJustification.__post_init__(self)
        object.__setattr__(self, "atom_substitution", MappingProxyType(dict(self.atom_substitution)))


@dataclass(frozen=True, slots=True)
class Sb(_ParentJustification):
    kind: ClassVar[str] = "Sb"
    direction: str
    occurrence_path: tuple[str, ...]

    def __post_init__(self) -> None:
        _ParentJustification.__post_init__(self)
        object.__setattr__(self, "occurrence_path", tuple(self.occurrence_path))


@dataclass(frozen=True, slots=True)
class Ad(_ParentJustification):
    kind: ClassVar[str] = "Ad"


@dataclass(frozen=True, slots=True)
class Smp(_ParentJustification):
    kind: ClassVar[str] = "Smp"


@dataclass(frozen=True, slots=True)
class DefinitionConversion(_ParentJustification):
    kind: ClassVar[str] = "definition_conversion"
    definition_id: str
    direction: str
    occurrence_path: tuple[str, ...]

    def __post_init__(self) -> None:
        _ParentJustification.__post_init__(self)
        object.__setattr__(self, "occurrence_path", tuple(self.occurrence_path))


Justification: TypeAlias = PostulateInstance | Sa | Sb | Ad | Smp | DefinitionConversion


@dataclass(frozen=True, slots=True)
class ProofNode:
    conclusion: Formula
    justification: Justification


@dataclass(frozen=True, slots=True)
class ProofCertificate:
    proof_id: str
    system: str
    basis_id: str
    goal: Formula
    root: str
    nodes: Mapping[str, ProofNode]

    def __post_init__(self) -> None:
        object.__setattr__(self, "nodes", MappingProxyType(dict(self.nodes)))
