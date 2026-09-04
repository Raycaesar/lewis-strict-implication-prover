# M0 Foundational Source Audit

This directory is the control center for the final source-level audit before
the trusted kernel (M1) is implemented.

The M0 structural validator answers questions such as:

> Does every system refer to registered schemas and rules?

The foundational source audit answers a different class of questions:

> Are those schemas, rules, definitions, system bases, and normalization
> decisions actually faithful to the selected Lewis & Langford calculus?

These two levels must not be conflated.

## Files

- `source_register.yaml` — machine-readable source/provenance register.
- `foundational_obligations.yaml` — closure register for M0 mathematical and
  historical obligations.
- `FIRST_PASS_FINDINGS.md` — first source pass and defects already identified.
- `FREEZE_CHECKLIST.md` — conditions for declaring `M0 FROZEN`.
- `WORK_MAX_FOUNDATIONAL_AUDIT_PROMPT.md` — read-only final audit prompt.
- `SPEC_REPAIR_NOTES.md` — exact safe repairs made or queued before freeze.

## Status vocabulary

- `source_verified`: checked directly against the cited source.
- `source_supported`: supported by a secondary syntactic source but still
  requires the project's own certificate/normalization decision.
- `open`: not yet resolved.
- `repair_needed`: current specification/documentation must change.
- `kernel_pending`: historical claim is supported, but a future machine proof
  or bridge certificate is still required.
- `blocked`: M0 must not be frozen while this remains unresolved.
- `not_in_m0`: deliberately outside scope.

## Freeze rule

`M0 FROZEN` may be declared only after:

1. all `blocked` obligations are closed;
2. every executable schema and primitive operation is source-verified;
3. all normalized bases are source-justified;
4. the definition/elaboration policy is deterministic;
5. structural and source-register CI pass;
6. a fresh Work Max foundational audit returns certification.
