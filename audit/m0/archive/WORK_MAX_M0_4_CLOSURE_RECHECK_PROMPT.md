# Work Max — second focused closure recheck of the M0.4 foundational repair

Execute this recheck now.

Repository:

`Raycaesar/lewis-strict-implication-prover`

Audit the exact repository state at the commit SHA supplied with this prompt.
Treat that commit as immutable.

This is a read-only closure recheck. Do not implement M1.

The previous closure recheck audited:

```text
5339a5a4f4c56a5e4feae3cc452730e488a309f1
```

and returned:

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

It found no P0 and confirmed that the schema/definition ASTs and normalized
S1–S5 basis memberships had not regressed. Certification failed only for two
P1 certificate/bridge defects and associated P2 provenance/validation defects.

## Required first-line verdict

Exactly one of:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

or

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

## Primary repair files

Read:

1. `audit/m0/M0_FOUNDATIONAL_CLOSURE_RECHECK_2026-09-04.md`
2. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.4.md`
3. `docs/FOUNDATIONAL_SPEC_v0.4.md`
4. `docs/PROOF_CERTIFICATE_SPEC.md`
5. `spec/rules.yaml`
6. `spec/systems.yaml`
7. `spec/schemas.yaml`
8. `audit/m0/source_register.yaml`
9. `audit/m0/foundational_obligations.yaml`
10. `audit/m0/certified_ast_fingerprints.yaml`
11. `scripts/validate_spec.py`
12. `scripts/validate_source_register.py`
13. `tests/spec/**`
14. `.github/workflows/m0-spec-validation.yml`
15. `AGENTS.md`

Do not redo the already-closed formula/source audit unless a locked AST changed.

## Mandatory questions

### A. P1-01 serialization closure

Verify that:

- top-level certificate fields are exact and closed;
- node fields are exact and closed;
- every justification kind has an exact allowed-field set;
- every unknown logical field is rejected;
- node IDs, root and parent references are nonempty strings;
- reference resolution uses exact string identity with no scalar coercion;
- duplicate mapping keys are rejected;
- no hidden metadata extension affects kernel validity.

Ask explicitly whether two independent M1 implementations are now forced to
accept the same logical certificate documents.

### B. P1-02 bridge direction

Verify the operational meaning of:

```text
from_basis_id
into_basis_id
```

and the invariant:

```text
expanded_certificate.basis_id == into_basis_id
```

Check exact S5 orientation:

```text
primary -> alternative : derive C11 under alternative
alternative -> primary : derive C10,C12 under primary
```

Reject certification if a characteristic axiom can be "bridged" merely by
checking it where it is already primitive.

### C. P2 provenance closure

Check every active Parry field identified by the previous audit.

All should state the reduced list:

```text
11.1-11.4, 11.6, 11.7, 30.1/A8
```

and the McKinsey derivation of 11.5.

Historical audit snapshots may preserve old wording as quoted history; active
normative/provenance fields may not.

### D. P2 freeze-gate closure

Run/inspect:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

Re-test the seven counter-mutations from the previous report. All must now fail
the freeze gate.

Also check:

- bridge-direction mutation;
- unknown-field mutation;
- integer/string reference-policy mutation;
- Parry-provenance mutation;
- fingerprint metadata mutation.

### E. P2 documentation/fingerprint closure

Check that:

- the v0.3 repair-log singular `parent` payload defect is corrected or clearly
  superseded;
- fingerprint lock metadata is validated;
- deliberate AST+hash edits remain documented as requiring re-audit;
- candidate→closed/frozen status transition is not blocked by the validator.

### F. Non-regression

Confirm no schema AST, definition AST or normalized basis membership changed.
The repair should remain certificate/provenance/validation-only.

## Certification standard

Certify if and only if:

1. no P0 remains;
2. no P1 remains;
3. no P2 remains that undermines freeze integrity;
4. independent implementations are forced to agree on logical certificate
   acceptance and S5 bridge orientation;
5. exact-SHA CI and validators/tests pass.

Do not withhold certification for optional P3 hardening.

If certified, explicitly state that M1 trusted-kernel implementation may begin.

Return one Markdown report.
