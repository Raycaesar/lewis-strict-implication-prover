# M0 Foundational Repair Log v0.4

**Repair basis:** focused closure recheck of commit  
`5339a5a4f4c56a5e4feae3cc452730e488a309f1`

**Input report:**  
`audit/m0/M0_FOUNDATIONAL_CLOSURE_RECHECK_2026-09-04.md`

**Scope:** narrow second repair. No stored schema AST, definition AST, or
normalized S1–S5 basis membership is changed.

## 1. P1-01 — closed certificate serialization

M0.4 closes the logical serialization under fields.

Top-level certificate fields are exactly:

```text
proof_id
system
basis_id
goal
root
nodes
```

Each node has exactly:

```text
conclusion
justification
```

Every justification kind declares one exact allowed-field set. Unknown fields
are rejected; there is no extension-by-ignoring policy.

Identifiers and references use nonempty strings. Root and parent references are
resolved by exact string identity with no integer/string coercion.

Duplicate mapping keys are rejected by the strict YAML loader.

No trusted metadata field exists in M0.4. Library/search provenance remains
outside the kernel certificate.

## 2. P1-02 — S5 bridge direction

The ambiguous fields:

```text
source_basis_id
target_basis_id
```

are removed from active S5 bridge records.

They are replaced by operational fields:

```text
from_basis_id
into_basis_id
```

Definition:

- `from_basis_id` = basis of the compact/source proof being translated;
- `into_basis_id` = basis in which the expanded native certificate checks.

Invariant:

```text
expanded_certificate.basis_id == into_basis_id
```

Correct S5 directions:

```text
C10_C12_DERIVE_C11:
  primary -> alternative
  recover C11 under alternative

C11_DERIVES_C10_C12:
  alternative -> primary
  recover C10,C12 under primary
```

This prevents the bridge from becoming trivial by checking a characteristic
axiom in the basis where it is already primitive.

## 3. P2-01 — complete Parry provenance repair

Every active M0.4 Parry S3 provenance field now states:

```text
11.1-11.4, 11.6, 11.7, 30.1/A8
```

with 11.5 supplied by the McKinsey derivation discussed on p. 138.

The previous shorthand saying that Parry literally takes all 11.1–11.7 as
primitive postulates is removed from active spec/source-register fields.

Historical audit snapshots are preserved as history and are not active
normative provenance.

## 4. P2-02 — freeze-gate hardening

`validate_spec.py --freeze` now structurally rejects all seven mutations
demonstrated by the second closure recheck:

1. postulate map domain changed to allow missing keys;
2. independent metavariable environments in definition conversion;
3. second implicit definition conversion allowed;
4. multi-occurrence `Sb`;
5. `atom.name` made traversable;
6. S5 bridge direction swapped;
7. unknown justification fields ignored.

It additionally validates:

- exact allowed fields per justification kind;
- nonempty-string node/reference type policy;
- exact reference identity;
- exact bridge expansion basis;
- fingerprint lock metadata.

`validate_source_register.py` checks every active Parry provenance field named
by the audit, not merely one source-register summary.

## 5. P2-03 — repair-log parent vocabulary

The superseded v0.3 log now uses the normative one-element:

```yaml
parents: [<node-id>]
```

rather than a singular `parent` logical payload.

## 6. P2-04 — fingerprint metadata

The fingerprint lock now records and freeze-validates:

```text
lock_version = 0.2
formula_source_audit_commit =
  4931e4daa124587a789ac27b841f499295facf5e

formula_nonregression_recheck_commit =
  5339a5a4f4c56a5e4feae3cc452730e488a309f1
```

The lock explicitly states that a deliberate AST+hash update cannot be
authenticated by the validator and requires human/Work Max re-audit.

## 7. Candidate/frozen status transition

Closure-candidate obligations may be:

```text
repair_implemented_reaudit_pending
```

After certification they may truthfully transition to:

```text
closed
```

The source-register validator accepts both in freeze checking, while
`frozen_source_audit` requires the second-repair obligations to be `closed`.

## 8. Repository hygiene

The active cleanup script is:

```text
scripts/apply_m0_v0_4_cleanup.sh
```

It uses `-exec rm` rather than the incompatible `find -prune ... -delete`
combination and removes materialized Windows `Zone.Identifier` files.

## 9. M1 gate

This repair does not authorize M1 by itself.

Upload the package, run all validation/tests and exact-SHA CI, then use:

```text
audit/m0/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md
```

M1 may begin only after:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
