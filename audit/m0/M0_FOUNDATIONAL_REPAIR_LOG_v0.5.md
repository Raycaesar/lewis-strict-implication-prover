# M0 Foundational Repair Log v0.5

**Repair basis:**  
`M0_FOUNDATIONAL_SECOND_CLOSURE_RECHECK_2026-09-05.md`

**Audited predecessor:**  
`5f86547a2f16e5f1e1620823e3b68457fb8350b7`

## 1. Why M0.4 failed

M0.4 correctly repaired the two former P1 defects, but its validator design was
wrong in one important respect.

Instead of replacing old certificate-semantics declarations with one canonical
representation, M0.4 added new policy mirrors beside the old declarations.
The validator checked the new mirrors while several old fields remained active.

Therefore an edit could change an old active declaration while leaving the new
mirror unchanged, and `--freeze` could still PASS.

The second closure recheck reproduced five such earlier semantic mutations and
four additional serialization mutations.

This is a P2 freeze-integrity defect, not a defect in the intended calculus.

## 2. M0.5 repair principle

M0.5 does not add another mirror.

It deletes the duplicate executable representations and establishes exactly
one machine-readable authority:

```text
spec/rules.yaml#canonical_certificate_contract
```

Former active top-level semantic registries are removed:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

The validator rejects reintroduction of any of those legacy keys.

## 3. What remains outside the canonical contract

`lewis_operations` contains historical/project provenance only:

```text
project_label
name
contract_kind
source
```

It may link a Lewis operation to the canonical kind but may not restate
executable semantics.

Human Markdown is explicitly nonnormative rendering. It cannot override the
canonical YAML.

## 4. Whole-contract fingerprint

M0.5 adds:

```text
audit/m0/certificate_contract_lock.yaml
```

It stores SHA-256 over the complete canonicalized
`canonical_certificate_contract` tree.

`validate_spec.py --freeze` recomputes the digest.

Thus any ordinary unreviewed semantic mutation anywhere in the single
authoritative contract fails the freeze gate, even if a dedicated field check
were accidentally omitted.

A deliberate simultaneous change to both contract and hash remains outside what
a local validator can authenticate; the lock explicitly declares such a change
foundational and requires focused independent re-audit.

## 5. Replayed M0.4 false positives

The M0.5 suite explicitly replays the nine mutations accepted by M0.4:

1. weaken postulate substitution to permit missing schema keys;
2. use independent environments in definition conversion;
3. permit a second implicit definition conversion;
4. allow multi-occurrence Sb;
5. make `atom.name` traversable;
6. add node metadata as a logical field;
7. permit extra node fields;
8. allow string-or-integer parent references;
9. make string identity coercive.

Each mutation changes the canonical contract and must be rejected in
`freeze=True`.

The suite additionally injects every removed legacy semantic registry into
`rules.yaml`; each injection must fail because the executable rules file itself
has an exact top-level key set.

## 6. Non-regression

M0.5 does not change:

- B1–B8;
- A8;
- C10–C12;
- DEF_OR;
- DEF_STRICT_IMP;
- DEF_EQUIV_S;
- normalized S1–S5 basis membership;
- operational S5 bridge direction.

No formula/source re-audit is requested.

## 7. Obligation status

The second closure recheck found no P0 and no P1.

Its one remaining P2 is represented by the M0.5 pending obligations:

```text
M0-V02
M0-V03
M0-FP03
```

These remain `repair_implemented_reaudit_pending` until the next exact-SHA
closure recheck. If certified, they may transition to `closed` and the source
register may transition to `frozen_source_audit`.

## 8. M1 gate

M1 remains forbidden until the exact M0.5 commit returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
