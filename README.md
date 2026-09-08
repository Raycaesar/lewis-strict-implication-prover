# Lewis S1–S5 Native Syntactic Prover

Native syntactic proof infrastructure for C. I. Lewis's strict-implication
systems S1–S5.

## Current status

**M0.6 foundational specification frozen.**

Work Max certified exact commit
`21117f3da827f873c3ed88b578a1681aabfca7ac` with the verdict
`M0 FOUNDATIONAL SPECIFICATION CERTIFIED`. The administrative freeze is now
recorded, and M1 trusted-kernel implementation may begin.

The formula/definition ASTs, normalized S1–S5 bases, and S5 bridge orientation
are unchanged.

## Sole certificate authority

The sole machine-readable certificate contract remains:

```text
spec/rules.yaml#canonical_certificate_contract
```

The document-decoding rule is a subtree of that same authority:

```text
spec/rules.yaml#canonical_certificate_contract.document_boundary
```

No `certificate_serialization` mirror or second executable certificate grammar
is reintroduced.

## Canonical trusted serialized form

M0.6 accepts exactly one trusted serialized certificate form at the kernel
boundary:

```text
strict UTF-8 JSON object
```

Duplicate object-member names are rejected recursively before construction of
the logical mapping. A first-wins/last-wins decoder is nonconforming.

Other import/UI formats may exist only outside the trusted boundary and must be
converted to this canonical JSON form first.

## Validation

Prefer:

```bash
bash scripts/run_m0_checks.sh
```

or, with the project virtual environment activated:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
python -m pytest
```

## M1 gate

The M1 gate is open following exact-SHA certification and this administrative
frozen-status transition.
