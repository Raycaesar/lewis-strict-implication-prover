# Lewis S1–S5 Native Syntactic Prover

A source-controlled, machine-checkable theorem prover project for the Lewis systems of strict implication S1–S5.

> **Search may be modern; every accepted proof must reduce to a certificate licensed by the selected normalized Lewis basis.**

## Current status

**M0.3 closure-audit candidate.**

The first independent foundational audit verified the formula/system layer but did not certify the certificate boundary. M0.3 freezes that boundary before any M1 implementation begins.

No automatic prover implementation is trusted yet.

## Canonical source

C. I. Lewis and C. H. Langford, *Symbolic Logic*, 2nd ed. (1932), using the supplied Dover reprint for page references.

## Notation

- preserve the Lewis fishhook for strict implication;
- use `equiv_s` / `\equiv_s`, never object-language `=`;
- keep metalanguage equality and `:=` separate;
- do not add Box to M0;
- exclude B9 from the initial core.

## Normalized bases

| System | Basis ID | Primitive schemas |
| --- | --- | --- |
| S1 | `S1_B1_B7` | B1–B7 |
| S2 | `S2_B1_B8` | B1–B8 |
| S3 | `S3_B1_B7_A8` | B1–B7 + A8 |
| S4 | `S4_B1_B7_C10` | B1–B7 + C10 |
| S5 primary | `S5_PRIMARY_B1_B7_C11` | B1–B7 + C11 |
| S5 alternative | `S5_ALT_B1_B7_C10_C12` | B1–B7 + C10 + C12 |

The two S5 bases are separate and are never unioned.

## Trusted certificate kinds

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Only `Sa`, `Sb`, `Ad`, and `Smp` are Lewis inference operations.

Definition conversion is an explicit checked metalinguistic certificate step, not an additional Lewis rule.

All Lewis primitive-rule matching uses exact surface ASTs.

## Executable M0 specification

```text
spec/
├── language.yaml
├── rules.yaml
├── schemas.yaml
└── systems.yaml
```

Normative certificate semantics: `docs/PROOF_CERTIFICATE_SPEC.md`.

Foundational overview: `docs/FOUNDATIONAL_SPEC_v0.3.md`.

## Validation

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

The `--freeze` modes are candidate-readiness checks. They do not replace the independent Work Max closure audit.

## M1 gate

M1 trusted-kernel implementation is forbidden until the exact M0.3 candidate commit receives:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
