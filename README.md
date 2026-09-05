# Lewis S1–S5 Native Syntactic Prover

Native syntactic proof infrastructure for C. I. Lewis's strict-implication
systems S1–S5.

## Current status

**M0.5 narrow P2 closure candidate.**

The second Work Max closure recheck found:

```text
P0: none
P1: none
P2: one freeze-integrity defect
```

M0.5 repairs only that P2. The formula/definition ASTs and normalized bases are
unchanged.

## Single certificate authority

The sole machine-readable certificate contract is:

```text
spec/rules.yaml#canonical_certificate_contract
```

Former duplicate semantic mirrors have been removed. Human certificate
documentation is explicitly nonnormative.

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
pytest
```

## M1 gate

M1 must not begin until the exact M0.5 candidate receives:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
