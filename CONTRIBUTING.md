# Contributing

This project is unusually strict about the distinction between:

1. the historical/formal specification;
2. the trusted proof checker;
3. untrusted proof-search machinery.

A contribution that blurs these layers will not be accepted even if it proves the intended formulas.

## Before contributing

Read:

- `AGENTS.md`
- `docs/FOUNDATIONAL_SPEC_v0.3.md`
- `docs/SOURCE_POLICY.md`
- `docs/ARCHITECTURE.md`
- `docs/PROOF_CERTIFICATE_SPEC.md`

## Types of changes

### A. Foundational changes

Examples:

- changing an axiom schema;
- changing S1–S5 bases;
- changing the language;
- adding a primitive inference rule;
- changing the role of `equiv_s`;
- adding `Box`;
- adding B9.

These require an explicit rationale, source evidence, and a new foundational audit.

### B. Kernel changes

Examples:

- parser-independent AST validation;
- schema matching;
- substitution checking;
- replacement-path checking;
- proof-DAG verification.

Kernel changes require adversarial rejection tests.

### C. Derived proof-library changes

A derived theorem or macro must include:

- source/provenance;
- declared minimal system;
- a fully checkable proof certificate;
- primitive-only expansion.

### D. Search changes

Search code is untrusted. It may generate candidates freely, but it must never bypass the kernel.

## Commit discipline

Prefer narrow commits such as:

```text
spec: clarify strict-equivalence representation
kernel: validate uniform substitution maps
proofs: add S1 proof of A7
search: add schema-directed forward expansion
docs: document C10/C12 to C11 bridge
```

Do not combine foundational changes with unrelated refactors.

Foundational certificate changes must update the M0 obligations register and pass both validator `--freeze` modes before closure audit.
