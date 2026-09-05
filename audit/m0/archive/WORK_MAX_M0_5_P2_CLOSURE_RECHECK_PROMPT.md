# Work Max — narrow P2 closure recheck of the M0.5 single-authority certificate repair

Execute this recheck now.

Repository:

`Raycaesar/lewis-strict-implication-prover`

Audit the exact repository state at the commit SHA supplied with this prompt.
Treat that commit as immutable.

This is read-only. Do not implement M1.

The previous second closure recheck audited:

```text
5f86547a2f16e5f1e1620823e3b68457fb8350b7
```

and returned:

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

It found:

```text
P0: none
P1: none
P2: one freeze-integrity defect
```

The exact candidate certificate semantics, S5 bridge direction, provenance,
schema/definition ASTs and normalized bases were otherwise accepted.

## Required first-line verdict

Exactly one:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

or

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

## Scope

This is a narrow recheck of the remaining P2 only.

Do not redo B1–C12 or the historical source audit unless a formula/definition
fingerprint or normalized basis membership changed.

Read:

1. `audit/m0/M0_FOUNDATIONAL_SECOND_CLOSURE_RECHECK_2026-09-05.md`
2. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.5.md`
3. `spec/rules.yaml`
4. `audit/m0/certificate_contract_lock.yaml`
5. `scripts/validate_spec.py`
6. `scripts/validate_source_register.py`
7. `tests/spec/**`
8. `docs/FOUNDATIONAL_SPEC_v0.5.md`
9. `docs/PROOF_CERTIFICATE_SPEC.md`
10. `AGENTS.md`
11. `audit/m0/foundational_obligations.yaml`
12. `audit/m0/source_register.yaml`
13. `spec/language.yaml`
14. `spec/schemas.yaml`
15. `spec/systems.yaml`

## Mandatory closure questions

### A. One authoritative representation

Verify that:

```text
spec/rules.yaml#canonical_certificate_contract
```

is now the sole active machine-readable certificate-semantics authority.

Confirm that the previous duplicate active registries have actually been
removed, not merely ignored:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

Check that reintroducing any one of them is rejected.

Check that `lewis_operations` contains provenance/link metadata only and cannot
carry additional executable semantics.

Check that Markdown certificate prose is explicitly nonnormative and cannot
override the canonical YAML.

### B. Replay all nine formerly accepted mutations

Independently mutate the sole canonical contract to reproduce:

1. postulate map permits missing keys;
2. definition conversion uses independent environments;
3. definition conversion permits a second implicit conversion;
4. Sb permits multiple replacements;
5. atom.name becomes traversable;
6. node metadata becomes a logical field;
7. extra node fields become permitted;
8. node references become string-or-integer;
9. string identity becomes coercive.

For every mutation require:

```text
validate_bundle(..., freeze=True) -> at least one issue
```

Do not accept mirror-only tests. Mutate the actual sole authoritative field.

### C. Whole-contract lock

Verify that `certificate_contract_lock.yaml` fingerprints the entire
canonical contract and that arbitrary unreviewed changes anywhere inside that
tree fail `--freeze`.

Confirm that the documented limitation is accurate: a deliberate simultaneous
contract+hash edit requires focused re-audit and is not claimed to be
cryptographically authenticated by the local validator.

### D. Internal contradiction check

Try to create contradictory certificate semantics by:

- adding a removed legacy registry;
- adding a semantic field to a `lewis_operations` entry;
- adding an unrecognized semantic extension inside the canonical contract.

The candidate must reject all three in freeze checking.

### E. Commands and CI

Run:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
git ls-files '*:Zone.Identifier'
```

Check exact-SHA GitHub Actions.

### F. Non-regression

Confirm no changes to:

- 12 stored schema ASTs;
- 3 definition ASTs;
- S1–S5 normalized basis membership;
- already-correct S5 bridge orientation.

## Certification standard

Certify if and only if the single remaining freeze-integrity P2 is closed and
no new P0/P1/freeze-undermining P2 is introduced.

Do not withhold certification for optional P3 hardening.

If certified, explicitly state that M0 may be frozen and M1 trusted-kernel
implementation may begin.

Return one Markdown report.
