# Work Max — narrow closure recheck of the M0.6 duplicate-key boundary repair

Execute this recheck now.

Repository:

`Raycaesar/lewis-strict-implication-prover`

Audit the exact repository state at the commit SHA supplied with this prompt.
Treat that commit as immutable.

This is read-only. Do not implement M1.

The previous narrow recheck audited:

```text
5436a3d2a8a7eecefc26712c2505f1b271c4c200
```

and returned:

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

It found:

```text
P0: none
P1: one certificate-document boundary regression
P2: one dependent freeze/accounting defect
```

All formula/definition ASTs, normalized bases, S5 bridge directions, the
single-authority repair, the nine former mutation repairs, local gates, and CI
were otherwise accepted.

## Required first-line verdict

Exactly one:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

or

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

## Narrow scope

Read primarily:

1. `audit/m0/M0_FOUNDATIONAL_P2_CLOSURE_RECHECK_2026-09-05.md`
2. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.6.md`
3. `spec/rules.yaml`
4. `scripts/validate_spec.py`
5. `scripts/certificate_document_conformance.py`
6. `tests/spec/test_certificate_document_boundary.py`
7. `audit/m0/certificate_contract_lock.yaml`
8. `audit/m0/foundational_obligations.yaml`
9. `audit/m0/source_register.yaml`
10. `docs/PROOF_CERTIFICATE_SPEC.md`
11. `docs/FOUNDATIONAL_SPEC_v0.6.md`
12. `.github/workflows/m0-spec-validation.yml`

Do not redo B1–C12, 11.01–11.03, S1–S5 basis, Parry, or S5 bridge audits unless
a protected object actually changed.

## Mandatory closure questions

### A. Sole-authority preservation

Verify that the duplicate-key repair lives inside the existing sole machine
authority:

```text
spec/rules.yaml#canonical_certificate_contract.document_boundary
```

and does not reintroduce `certificate_serialization` or another active mirror.

### B. Exact serialized document boundary

Determine whether independent M1 implementations are now forced to agree on
the accepted serialized certificate documents.

Check that M0.6 fixes exactly one trusted serialized format and requires:

- strict UTF-8 decoding;
- a top-level JSON object;
- recursive duplicate object-member rejection;
- duplicate detection before any first-wins/last-wins map collapse;
- exact decoded-string identity for member-name comparison;
- rejection of nonstandard NaN/Infinity constants;
- the stated BOM, Unicode-scalar-string, and decoded-value-type policy;
- logical certificate validation only after strict decoding succeeds.

If another frontend format is permitted, confirm it is explicitly outside the
trusted M0 certificate boundary and cannot enlarge the kernel's serialized
certificate acceptance set.

### C. Duplicate-key conformance probes

Run/inspect the direct document fixtures. At minimum independently verify:

```text
duplicate root                 -> reject
duplicate nested kind          -> reject
duplicate nested formula field -> reject
duplicate key equal only after JSON escape decoding -> reject
```

Also mutate the canonical duplicate-key policy to an accepting behavior and
confirm `validate_bundle(..., freeze=True)` rejects it.

### D. Whole-contract lock

Recompute the contract SHA-256 independently and verify the lock covers the new
document boundary.

Confirm that a mutation of the duplicate-key canonical field breaks the freeze
lock.

### E. Audit accounting

Check that `M0-C05` was correctly reopened and the new boundary/validator/lock
repairs remain `repair_implemented_reaudit_pending` rather than falsely closed.

Check that the post-certification transition can still truthfully close them.

### F. Commands and exact-SHA CI

Run/inspect:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
git ls-files '*:Zone.Identifier'
```

and exact-SHA GitHub Actions.

### G. Non-regression

Confirm no schema AST, definition AST, normalized basis membership, or S5 bridge
record changed relative to `5436a3d2...` except version metadata.

## Certification standard

Certify if and only if:

1. the lost duplicate-key serialization invariant is fully restored in the sole
   authority;
2. the serialized document boundary is deterministic across independent
   implementations;
3. direct duplicate-key documents are rejected before mapping construction;
4. freeze validation and the whole-contract lock protect the restored field;
5. no new P0/P1 exists and no P2 undermines freeze integrity;
6. exact-SHA gates and CI pass.

Do not manufacture a broader objection or reopen already certified formula/source
layers merely because this is another closure pass.

If certified, explicitly state that M0 may be frozen and M1 trusted-kernel
implementation may begin after the administrative frozen-status commit.

Return one Markdown report.
