# Lewis S1–S5 Native Syntactic Prover

Native syntactic proof infrastructure for C. I. Lewis's strict-implication
systems S1–S5.

> **Search may be modern; every accepted theorem must reduce to a certificate
> licensed by the selected normalized Lewis basis.**

## Current status

**M0.4 second-closure-audit candidate.**

The first closure recheck confirmed the formula/system layer and closed the
definition-conversion, schema-instantiation/Sa, occurrence-path, and primitive
S5 basis issues. M0.4 closes the remaining certificate-serialization,
bridge-direction, provenance, and freeze-gate defects.

M1 implementation is still forbidden until an independent exact-SHA recheck
returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

## Active specification

- `docs/FOUNDATIONAL_SPEC_v0.4.md`
- `docs/PROOF_CERTIFICATE_SPEC.md`
- `spec/language.yaml`
- `spec/rules.yaml`
- `spec/schemas.yaml`
- `spec/systems.yaml`

## Normalized bases

| System | Basis ID | Primitive schemas |
| --- | --- | --- |
| S1 | `S1_B1_B7` | B1–B7 |
| S2 | `S2_B1_B8` | B1–B8 |
| S3 | `S3_B1_B7_A8` | B1–B7 + A8 |
| S4 | `S4_B1_B7_C10` | B1–B7 + C10 |
| S5 primary | `S5_PRIMARY_B1_B7_C11` | B1–B7 + C11 |
| S5 alternative | `S5_ALT_B1_B7_C10_C12` | B1–B7 + C10 + C12 |

## Trusted certificate kinds

Exactly:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Certificate objects are closed-world. Unknown logical fields are rejected.
Node IDs and references are nonempty strings resolved by exact string identity.

## Validation

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```
