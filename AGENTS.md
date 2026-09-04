# AGENTS.md

## Current milestone

This repository is an **M0.4 second-closure-audit candidate**.

Do not implement M1 until the exact candidate commit is independently certified.

## Normative read order

1. `docs/FOUNDATIONAL_SPEC_v0.4.md`
2. `docs/PROOF_CERTIFICATE_SPEC.md`
3. `docs/SOURCE_POLICY.md`
4. `spec/language.yaml`
5. `spec/rules.yaml`
6. `spec/schemas.yaml`
7. `spec/systems.yaml`
8. `audit/m0/source_register.yaml`
9. `audit/m0/foundational_obligations.yaml`
10. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.4.md`

If these disagree, stop and report the conflict.

## Trusted boundary

Only these certificate kinds exist at the kernel boundary:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Only `Sa`, `Sb`, `Ad`, and `Smp` are Lewis inference operations.

All logical certificate objects are closed-world. Unknown fields are rejected.

Node IDs/root/parent references are nonempty strings. Never coerce integers to
strings or normalize identifiers before reference lookup.

## Definitions

No Lewis rule silently expands `or`, `strict_imp`, or `equiv_s`.

Visible definitional change requires one explicit `definition_conversion`
acting at one occurrence with one shared metavariable environment.

## Basis and bridges

Every proof declares `basis_id`.

Never union the two S5 bases.

Bridge fields are operational:

```text
from_basis_id
into_basis_id
```

The expanded native certificate must have:

```text
basis_id == into_basis_id
```

For S5:

```text
primary -> alternative : recover C11 under the alternative basis
alternative -> primary : recover C10,C12 under the primary basis
```

## Forbidden shortcuts

Do not add:

- unrestricted necessitation;
- Box to M0;
- B9 to M0;
- object-language `=`;
- implicit definition conversion;
- semantic/tableau/sequent proof steps;
- modern normal-modal axioms as substitutes;
- mixed-basis S5 checking;
- unknown-field-tolerant certificate parsing.

## Formula regression lock

The source-audited schema/definition ASTs are locked by
`audit/m0/certified_ast_fingerprints.yaml`.

Any AST/hash/lock-metadata edit requires explicit foundational re-audit.
