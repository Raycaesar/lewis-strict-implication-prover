# Lewis S1–S5 Native Syntactic Prover
## Foundational specification v0.4

**Status:** M0 second-closure-audit candidate  
**Canonical historical source:** Lewis & Langford, *Symbolic Logic* (1932)  
**Executable specification:** `spec/*.yaml`

## 1. Logical layer

The formula/system layer is unchanged from the independently audited candidate:

```text
B1–B8
A8
C10–C12
DEF_OR
DEF_STRICT_IMP
DEF_EQUIV_S
```

Normalized bases remain:

```text
S1 = B1–B7
S2 = B1–B8
S3 = B1–B7 + A8
S4 = B1–B7 + C10
S5 primary = B1–B7 + C11
S5 alternative = B1–B7 + C10 + C12
```

No Box, B9, unrestricted necessitation, or modern replacement calculus is added.

## 2. Surface syntax and definitions

Primitive/core formula constructors:

```text
atom
neg
and
poss
```

First-class defined surface constructors:

```text
or
strict_imp
equiv_s
```

The Lewis fishhook is preserved. Strict equivalence is rendered as `equiv_s`,
never object-language `=`.

Visible use of 11.01–11.03 requires an explicit checked
`definition_conversion`. Lewis rule matching is exact on the surface AST.

## 3. Closed-world certificate serialization

The trusted certificate object is closed-world.

Top-level logical fields are exactly:

```text
proof_id
system
basis_id
goal
root
nodes
```

No other top-level field is admitted by M0.4.

Each node has exactly:

```text
conclusion
justification
```

Every justification kind has an exact allowed-field set. Unknown fields are
rejected rather than ignored.

Identifiers and references are nonempty strings. No numeric/string coercion,
Unicode normalization, or implicit identifier conversion occurs; references
resolve by exact string identity.

Duplicate YAML/JSON mapping keys are rejected before logical checking.

## 4. Trusted certificate kinds

Exactly:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Only `Sa`, `Sb`, `Ad`, `Smp` are Lewis inference operations.

`definition_conversion` is a trusted metalinguistic certificate check, not a
fifth Lewis rule.

## 5. Postulate instance and Sa

`postulate_instance` is parentless and substitutes exactly the schema
metavariables occurring in the selected primitive schema.

`Sa` has exactly one theorem parent and substitutes a nonempty subset of object
atom names occurring in that parent.

`Sa` is:

```text
simultaneous
one-pass
nonrecursive into replacement values
```

Missing/extra schema metavariable keys are rejected. Sa keys not occurring in
the parent are rejected. Unmentioned object atoms are fixed.

## 6. Occurrence paths and one-occurrence discipline

`Sb` and `definition_conversion` share one path grammar.

Logical paths are lists over:

```text
arg
left
right
```

Root is `[]`. `atom.name` is never traversable.

No definition expansion occurs during path traversal.

Each primitive `Sb` or `definition_conversion` node changes exactly one
selected occurrence.

## 7. Definition conversion

One `definition_conversion` node uses:

```text
parents: [<one-node-id>]
definition_id
direction
occurrence_path
```

Direction is `expand` or `contract`.

The matcher uses one shared metavariable environment. Repeated metavariables
must match structurally. No second implicit conversion is allowed.

## 8. Basis identity

Every proof declares one stable `basis_id`.

```text
S1_B1_B7
S2_B1_B8
S3_B1_B7_A8
S4_B1_B7_C10
S5_PRIMARY_B1_B7_C11
S5_ALT_B1_B7_C10_C12
```

The S5 bases are never unioned.

## 9. Operational bridge direction

Bridge fields are:

```text
from_basis_id
into_basis_id
```

They are operational, not merely descriptive.

`from_basis_id` is the basis of the compact/source proof being translated.

`into_basis_id` is the basis in which the expanded native bridge certificate
must check.

Therefore:

```text
expanded_certificate.basis_id == into_basis_id
```

For S5:

```text
C10_C12_DERIVE_C11:
  from  = S5_PRIMARY_B1_B7_C11
  into  = S5_ALT_B1_B7_C10_C12
  recover C11 in the alternative basis

C11_DERIVES_C10_C12:
  from  = S5_ALT_B1_B7_C10_C12
  into  = S5_PRIMARY_B1_B7_C11
  recover C10 and C12 in the primary basis
```

This direction prevents a bridge from "proving" an axiom in the basis where it
is already primitive.

## 10. Parry provenance

Parry 1939 pp. 137–138 is described uniformly as follows:

> Parry displays the reduced S3 postulate list 11.1–11.4, 11.6, 11.7 and
> 30.1/A8; 11.5 is supplied by the McKinsey derivation discussed on p. 138.
> This directly supports the project's unreduced normalized B1–B7+A8 basis.

No active M0.4 field says that Parry literally prints all 11.1–11.7 as
primitive postulates.

## 11. L&L p. 498 / p. 501 provenance

The p. 498 derivability items are recorded with that paragraph's explicit
A1–A8/B1–B9 background qualification.

L&L p. 501 is the canonical direct source for the two B1–B7-based S5
presentations.

Historical statements do not replace native bridge certificates.

## 12. Fingerprint lock

`audit/m0/certified_ast_fingerprints.yaml` locks the source-audited schema and
definition ASTs.

The freeze validator checks:

- lock version;
- formula-source-audit commit;
- formula-nonregression-recheck commit;
- all stored hashes.

A deliberate AST+hash edit cannot be authenticated by the validator alone and
therefore remains a mandatory foundational re-audit event.

## 13. M1 gate

M1 may begin only after:

```text
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

all pass on the exact candidate commit, GitHub Actions is green, and a focused
independent closure recheck returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
