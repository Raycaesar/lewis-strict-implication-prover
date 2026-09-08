"""Trusted structural operations over exact surface formulas.

All registries come from a ``FrozenSpec`` returned by ``load_frozen_spec``.
These operations return formulas/environments, never accepted proof steps.
They neither check theorem provenance or basis admission nor invoke logical
rules or diagnostic erasure. Defined nodes remain first-class surface nodes.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from lewis_prover.errors import (
    AtomSubstitutionError, DefinitionConversionError, OccurrencePathError,
    SchemaInstantiationError, SchemaMatchError, StructuralTransformError,
)
from lewis_prover.syntax.formula import And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp

from .model import FrozenSpec

# Constructor adapters only; no schema, definition, or path semantics live here.
_CONSTRUCTORS = {cls.op: cls for cls in (Atom, Neg, And, Poss, Or, StrictImp, EquivS)}
OccurrencePath = list[str] | tuple[str, ...]


def _children(formula: Formula, spec: FrozenSpec) -> tuple[str, ...]:
    return spec.canonical_certificate_contract["occurrence_path"]["traversable_fields"][formula.op]


def _check_formula(value: Any, spec: FrozenSpec, error: type[StructuralTransformError]) -> None:
    """Reject raw/meta ASTs and unknown Formula subclasses, including at depth."""
    pending = [(value, False)]
    active: set[int] = set()
    done: set[int] = set()
    while pending:
        node, exiting = pending.pop()
        identity = id(node)
        if exiting:
            active.remove(identity)
            done.add(identity)
            continue
        if identity in active:
            raise error("object formula contains a cycle")
        if identity in done:
            continue
        if type(node) not in _CONSTRUCTORS.values():
            raise error("expected an object Formula, not a schema metavariable or raw AST")
        if type(node) is Atom:
            if not isinstance(node.name, str) or not node.name:
                raise error("object atom name must be a nonempty string")
            done.add(identity)
            continue
        active.add(identity)
        pending.append((node, True))
        pending.extend((getattr(node, field), False) for field in _children(node, spec))


def _schema(schema_id: str, spec: FrozenSpec, error: type[StructuralTransformError]) -> Mapping[str, Any]:
    registry = spec.schemas["schemas"]
    if not isinstance(schema_id, str) or schema_id not in registry:
        raise error(f"unknown registered schema: {schema_id!r}")
    return registry[schema_id]["ast"]


def _metavariables(pattern: Mapping[str, Any]) -> frozenset[str]:
    if set(pattern) == {"meta"}:
        return frozenset({pattern["meta"]})
    names: set[str] = set()
    for child in pattern.values():
        if isinstance(child, Mapping):
            names.update(_metavariables(child))
    return frozenset(names)


def _environment(
    substitution: Mapping[str, Formula], spec: FrozenSpec, error: type[StructuralTransformError]
) -> dict[str, Formula]:
    if not isinstance(substitution, Mapping):
        raise error("substitution must be a mapping from names to object formulas")
    snapshot = dict(substitution)
    for key, value in snapshot.items():
        if not isinstance(key, str) or not key:
            raise error("substitution keys must be nonempty names in the required namespace")
        _check_formula(value, spec, error)
    return snapshot


def _instantiate(pattern: Mapping[str, Any], environment: Mapping[str, Formula], spec: FrozenSpec) -> Formula:
    if set(pattern) == {"meta"}:
        # Return the replacement unchanged: its atoms are not schema holes.
        return environment[pattern["meta"]]
    op = pattern["op"]
    if op == "atom":
        return Atom(pattern["name"])
    fields = spec.language["formula_ast"][op]["fields"]
    return _CONSTRUCTORS[op](**{field: _instantiate(pattern[field], environment, spec) for field in fields})


def _match(
    pattern: Mapping[str, Any], actual: Formula, environment: dict[str, Formula],
    spec: FrozenSpec, error: type[StructuralTransformError],
) -> None:
    if set(pattern) == {"meta"}:
        name = pattern["meta"]
        if name in environment and environment[name] != actual:
            raise error(f"inconsistent repeated schema metavariable {name!r}")
        environment.setdefault(name, actual)
        return
    if pattern["op"] != actual.op:
        raise error("selected surface formula does not match the registered pattern")
    if type(actual) is Atom:
        if pattern["name"] != actual.name:
            raise error("object atom differs from the registered literal atom")
        return
    for field in spec.language["formula_ast"][pattern["op"]]["fields"]:
        _match(pattern[field], getattr(actual, field), environment, spec, error)


def schema_metavariables(schema_id: str, frozen_spec: FrozenSpec) -> frozenset[str]:
    """Return schema holes only; object atom names are a separate namespace."""
    return _metavariables(_schema(schema_id, frozen_spec, SchemaInstantiationError))


def instantiate_schema(
    schema_id: str, substitution: Mapping[str, Formula], frozen_spec: FrozenSpec,
) -> Formula:
    """Instantiate a registered schema with exactly its metavariable domain."""
    pattern = _schema(schema_id, frozen_spec, SchemaInstantiationError)
    environment = _environment(substitution, frozen_spec, SchemaInstantiationError)
    required = _metavariables(pattern)
    missing, extra = required - environment.keys(), environment.keys() - required
    if missing or extra:
        raise SchemaInstantiationError(f"schema map domain mismatch: missing {sorted(missing)}, extra {sorted(extra)}")
    return _instantiate(pattern, environment, frozen_spec)


def match_schema(schema_id: str, formula: Formula, frozen_spec: FrozenSpec) -> Mapping[str, Formula]:
    """Match a registered schema once; return an immutable shared environment."""
    pattern = _schema(schema_id, frozen_spec, SchemaMatchError)
    _check_formula(formula, frozen_spec, SchemaMatchError)
    environment: dict[str, Formula] = {}
    _match(pattern, formula, environment, frozen_spec, SchemaMatchError)
    return MappingProxyType(environment)


def object_atom_names(formula: Formula, frozen_spec: FrozenSpec) -> frozenset[str]:
    """Collect names from object atoms, including atoms under defined nodes."""
    _check_formula(formula, frozen_spec, AtomSubstitutionError)
    names: set[str] = set()
    seen: set[int] = set()
    pending = [formula]
    while pending:
        node = pending.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        if type(node) is Atom:
            names.add(node.name)
        else:
            pending.extend(getattr(node, field) for field in _children(node, frozen_spec))
    return frozenset(names)


def substitute_atoms(
    source: Formula, substitution: Mapping[str, Formula], frozen_spec: FrozenSpec,
) -> Formula:
    """Apply Sa's nonempty subset map simultaneously, once, on object atoms.

    The source is only a formula here; its status as an established theorem is
    the later checker's responsibility. Replacement values are never revisited.
    """
    atoms = object_atom_names(source, frozen_spec)
    environment = _environment(substitution, frozen_spec, AtomSubstitutionError)
    if not environment or environment.keys() - atoms:
        raise AtomSubstitutionError("Sa map must be a nonempty subset of the source object atoms")

    def visit(node: Formula) -> Formula:
        if type(node) is Atom:
            return environment.get(node.name, node)
        return type(node)(**{field: visit(getattr(node, field)) for field in _children(node, frozen_spec)})

    return visit(source)


def _path(path: OccurrencePath, spec: FrozenSpec) -> tuple[str, ...]:
    # JSON input uses a list; certificate models preserve that list as a tuple.
    # Other sequences, strings, wildcards, and lists of paths are not a path.
    if not isinstance(path, (list, tuple)):
        raise OccurrencePathError("occurrence path must be a list (or its immutable tuple representation)")
    path = tuple(path)
    legal = spec.canonical_certificate_contract["occurrence_path"]["legal_segments"]
    if any(not isinstance(segment, str) or segment not in legal for segment in path):
        raise OccurrencePathError("occurrence path contains an invalid segment")
    return path


def _locate(
    source: Formula, path: tuple[str, ...], spec: FrozenSpec,
) -> tuple[Formula, list[tuple[Formula, str]]]:
    selected = source
    ancestors: list[tuple[Formula, str]] = []
    for segment in path:
        if segment not in _children(selected, spec):
            raise OccurrencePathError(f"{selected.op} has no traversable child {segment!r}")
        ancestors.append((selected, segment))
        selected = getattr(selected, segment)
    return selected, ancestors


def resolve_occurrence(source: Formula, path: OccurrencePath, frozen_spec: FrozenSpec) -> Formula:
    """Select exactly one surface subtree without expanding any definitions."""
    _check_formula(source, frozen_spec, OccurrencePathError)
    selected, _ = _locate(source, _path(path, frozen_spec), frozen_spec)
    return selected


def replace_occurrence(
    source: Formula, path: OccurrencePath, replacement: Formula, frozen_spec: FrozenSpec,
) -> Formula:
    """Rebuild only ancestors of one selected occurrence, even with shared nodes."""
    _check_formula(source, frozen_spec, OccurrencePathError)
    _check_formula(replacement, frozen_spec, OccurrencePathError)
    _, ancestors = _locate(source, _path(path, frozen_spec), frozen_spec)
    result = replacement
    for parent, segment in reversed(ancestors):
        children = {field: getattr(parent, field) for field in _children(parent, frozen_spec)}
        children[segment] = result
        result = type(parent)(**children)
    return result


def convert_definition(
    source: Formula, definition_id: str, direction: str, path: OccurrencePath, frozen_spec: FrozenSpec,
) -> Formula:
    """Perform exactly one registered expansion/contraction at the given path.

    Matching and instantiation share a single metavariable environment. The
    output side is instantiated once, including any defined surface nodes it
    contains. No nested conversion, Sb operation, or rule acceptance occurs.
    """
    registry = frozen_spec.language["metadefinitions"]
    if not isinstance(definition_id, str) or definition_id not in registry:
        raise DefinitionConversionError(f"unknown registered definition: {definition_id!r}")
    allowed_directions = frozen_spec.canonical_certificate_contract["kinds"]["definition_conversion"]["direction_values"]
    if not isinstance(direction, str) or direction not in allowed_directions:
        raise DefinitionConversionError(f"invalid definition conversion direction: {direction!r}")
    path = _path(path, frozen_spec)
    selected = resolve_occurrence(source, path, frozen_spec)
    definition = registry[definition_id]
    from_side, to_side = ("lhs", "rhs") if direction == "expand" else ("rhs", "lhs")
    environment: dict[str, Formula] = {}
    _match(definition[from_side], selected, environment, frozen_spec, DefinitionConversionError)
    replacement = _instantiate(definition[to_side], environment, frozen_spec)
    return replace_occurrence(source, path, replacement, frozen_spec)
