# Proof Certificate Specification
## M0.4 normative candidate

## 1. Closed-world principle

The trusted logical certificate serialization is closed-world.

Unknown fields are rejected at every logical object layer. There is no
"ignore unknown justification field" option.

Top-level fields are exactly:

```yaml
proof_id: <nonempty string>
system: <nonempty string>
basis_id: <nonempty string>
goal: <object formula AST>
root: <nonempty string node id>
nodes: <mapping from nonempty string node ids to nodes>
```

Each node is exactly:

```yaml
conclusion: <object formula AST>
justification: <justification object>
```

Node IDs, root, and parent references are nonempty strings. Reference equality
is exact string equality with no scalar coercion.

Duplicate mapping keys are rejected before logical checking.

## 2. Exact justification schemas

### `postulate_instance`

Allowed fields are exactly:

```yaml
kind: postulate_instance
schema_id: <nonempty string>
schema_substitution: <mapping>
```

No `parents` field is allowed.

The schema-substitution domain is exactly the schema metavariable set of the
registered schema. Missing and extra keys are rejected.

### `Sa`

Allowed fields are exactly:

```yaml
kind: Sa
parents: [<one node id>]
atom_substitution: <mapping>
```

The map domain is a nonempty subset of object atoms occurring in the parent.
Extra/nonoccurring keys are rejected.

Application is simultaneous, one-pass, nonrecursive into replacement values.
Unmentioned atoms are fixed.

### `Sb`

Allowed fields are exactly:

```yaml
kind: Sb
parents: [<equivalence node id>, <target node id>]
direction: left_to_right | right_to_left
occurrence_path: <path>
```

The first parent must have exact surface root `equiv_s`.

Exactly one selected occurrence is replaced.

No implicit definition conversion is allowed.

### `Ad`

Allowed fields are exactly:

```yaml
kind: Ad
parents: [<left node id>, <right node id>]
```

Conclusion is exactly the ordered surface conjunction of the two parent
conclusions.

### `Smp`

Allowed fields are exactly:

```yaml
kind: Smp
parents: [<antecedent node id>, <strict-implication node id>]
```

The second parent must have exact surface root `strict_imp(A,B)` and `A` must
be structurally identical to the first parent conclusion.

### `definition_conversion`

Allowed fields are exactly:

```yaml
kind: definition_conversion
parents: [<one node id>]
definition_id: <nonempty string>
direction: expand | contract
occurrence_path: <path>
```

Exactly one occurrence is changed.

One shared metavariable environment is used. Repeated metavariables require
exact structural identity.

No nested/second implicit conversion is permitted.

## 3. Occurrence-path grammar

Paths are lists of strings.

Root:

```yaml
[]
```

Legal segments:

```text
arg
left
right
```

Traversable formula fields are exactly:

```text
neg:        arg
poss:       arg
and:        left,right
or:         left,right
strict_imp: left,right
equiv_s:    left,right
atom:       none
```

`atom.name` is data, not a formula child.

Defined nodes are traversed as visible surface nodes. No definition expansion
occurs during traversal.

## 4. Surface identity

All Lewis primitive operations use exact surface AST identity.

Full erasure of definitions is diagnostic only and never rescues a failed
primitive-rule application.

## 5. Proof DAG

The checker rejects unless:

- every node-map key is a nonempty string;
- every parent/root reference is a nonempty string;
- every reference resolves by exact string identity;
- the dependency graph is acyclic;
- every node is reachable from root;
- every node is accepted after its parents;
- root conclusion equals goal structurally.

No line-number field is part of the logical certificate.

## 6. Basis discipline

Every proof declares one allowed `(system,basis_id)` pair.

S5 primary and alternative bases are never unioned.

A `postulate_instance` is admitted only when `schema_id` belongs to the exact
primitive schema set of the declared `basis_id`.

## 7. Bridge semantics

Compact bridge/library objects are outside the primitive kernel vocabulary.

Their operational fields are:

```yaml
from_basis_id: ...
into_basis_id: ...
```

The expanded native certificate must satisfy:

```text
expanded_certificate.basis_id == into_basis_id
```

A bridge must recover every primitive available in `from_basis_id` but absent
from `into_basis_id` that the translated proof actually needs.

For the two S5 bridge obligations:

```text
primary -> alternative : derive C11 under alternative
alternative -> primary : derive C10,C12 under primary
```

## 8. Metadata

M0.4 trusted logical certificate objects contain no metadata field.

Source/provenance/search metadata belongs outside the kernel certificate and
cannot change certificate validity.

## 9. Primitive proof rendering

A primitive proof may retain fishhook and `equiv_s`.

"Primitive" concerns proof operations, not erasure of all defined notation.

A separate fully-erased diagnostic view may recursively expand definitions.
