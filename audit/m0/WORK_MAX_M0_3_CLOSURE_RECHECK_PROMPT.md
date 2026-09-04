# Work Max — focused closure recheck of the M0.3 foundational repair

Execute this recheck now.

Repository:

`Raycaesar/lewis-strict-implication-prover`

Audit the exact repository state at the commit SHA supplied with this prompt.
Treat that commit as immutable. Do not audit a later state of `main`.

This is a **read-only closure recheck**, not a new prover implementation task.

The previous foundational audit of commit

```text
4931e4daa124587a789ac27b841f499295facf5e
```

returned:

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

but explicitly found that the stored schema ASTs and normalized S1–S5 bases did
not require mathematical replacement.

The M0.3 repair is intended to close the previous P0/P1 certificate-boundary
defects and associated P2 provenance/validation defects.

## Required first-line verdict

The first line must be exactly one of:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

or

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

No intermediate verdict.

## Primary files to inspect

Read:

1. `audit/m0/M0_FOUNDATIONAL_AUDIT_2026-09-04.md`
2. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.3.md`
3. `docs/FOUNDATIONAL_SPEC_v0.3.md`
4. `docs/PROOF_CERTIFICATE_SPEC.md`
5. `docs/ARCHITECTURE.md`
6. `AGENTS.md`
7. `spec/language.yaml`
8. `spec/rules.yaml`
9. `spec/systems.yaml`
10. `spec/schemas.yaml`
11. `audit/m0/source_register.yaml`
12. `audit/m0/foundational_obligations.yaml`
13. `audit/m0/certified_ast_fingerprints.yaml`
14. `.github/workflows/m0-spec-validation.yml`
15. `scripts/validate_spec.py`
16. `scripts/validate_source_register.py`
17. `tests/spec/**`

Use L&L, Parry, Feys, and the supplied historical sources only as needed to
check regression or source-provenance repairs.

Do **not** redo a full formula-by-formula audit merely for formality unless a
repair changed or invalidated the previously certified formula/system layer.

## Mandatory closure questions

### A. P0 closure — definition conversion

Determine whether M0.3 now uniquely specifies a sound trusted mechanism for:

- DEF_OR;
- DEF_STRICT_IMP;
- DEF_EQUIV_S.

Check that:

- no Lewis primitive rule performs implicit definition expansion;
- all primitive-rule matching uses exact surface AST;
- `definition_conversion` is explicit and deterministic;
- it is correctly classified as metalinguistic certificate checking rather than
  a fifth Lewis inference rule;
- one consistent metavariable environment is used;
- exactly one occurrence is changed;
- the design does not create circularity with `Sb`.

If two reasonable M1 implementers could still accept different certificate
sets while claiming compliance, certification must fail.

### B. P1 closure — postulate instance versus Sa

Verify that:

- schema metavariables and object atoms are disjoint namespaces;
- `postulate_instance` is parentless;
- its map domain is exact;
- `Sa` is a one-parent theorem operation;
- Sa is simultaneous, one-pass, nonrecursive;
- the renderer no longer disguises a direct schema instance as Sa.

### C. P1 closure — occurrence paths

Verify that a single normative path grammar exists and is used by both `Sb`
and `definition_conversion`.

Check root paths, unary/binary fields, invalid atom paths, and exact one-
occurrence replacement.

### D. P1 closure — S5 basis identity

Verify that every proof has a stable `basis_id`.

Check that:

- primary S5 admits C11 but not C10/C12 primitively;
- alternative S5 admits C10/C12 but not C11 primitively;
- no union basis exists;
- future bridges are source/target-basis explicit.

### E. Formula/system non-regression

Verify that the repair did not silently alter:

- B1–B8;
- A8;
- C10–C12;
- 11.01–11.03;
- normalized S1–S5 schema membership.

Check the AST fingerprint mechanism for usefulness and limitations.

### F. Source/provenance closure

Check that:

- Parry 1939 is now described accurately;
- p. 498 derivability claims preserve their background qualification;
- p. 501 is used as the canonical direct source for the B1–B7-based S5 bases.

### G. Validator and CI closure

Run or inspect:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

Check whether the validators genuinely test the repaired invariants rather than
merely asserting constants.

Inspect mutation/rejection tests.

Check CI coverage and Zone.Identifier rejection.

## Defect classification

Use:

- P0 — foundational blocker;
- P1 — major specification/certificate defect;
- P2 — local validation/provenance/documentation defect;
- P3 — optional improvement.

Do not withhold certification for a merely optional P3 improvement.

## Certification standard

Certify M0 if and only if:

1. the logical/formula layer remains intact;
2. the trusted certificate semantics are deterministic enough for independent
   implementations to agree;
3. no P0/P1 defect remains;
4. no unresolved P2 defect undermines freeze integrity;
5. the exact candidate commit may safely serve as the immutable logical basis
   for M1.

If certified, explicitly state that M1 trusted-kernel implementation may begin.

Return one Markdown report.
