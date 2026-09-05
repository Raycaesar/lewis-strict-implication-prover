# Lewis S1–S5 Native Syntactic Prover

Native syntactic proof infrastructure for C. I. Lewis's strict-implication
systems S1–S5.

## Current status

**M0.6 narrow certificate-document-boundary closure candidate.**

The latest Work Max recheck of the M0.5 candidate found:

```text
P0: none
P1: one certificate-document boundary regression
P2: one dependent freeze/accounting defect
```

The exact defect was narrow: M0.5 correctly created one machine-readable
certificate authority, but while deleting the old duplicate registry it failed
to migrate the already accepted rule that duplicate serialized mapping/object
keys must be rejected before logical checking.

M0.6 restores that rule **inside the existing sole authority** and adds a
canonical document-decoding boundary plus direct document-level rejection
tests.

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

M1 must not begin until an exact-SHA M0.6 closure recheck returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
