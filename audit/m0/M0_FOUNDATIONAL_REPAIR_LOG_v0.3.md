# Historical v0.3 repair record

This file records the superseded M0.3 candidate. Its certificate example uses the normative one-element `parents` list; current bridge semantics and serialization are in M0.4.

---

# M0 Foundational Repair Log v0.3

**Repair basis:** Work Max audit  
`audit/m0/M0_FOUNDATIONAL_AUDIT_2026-09-04.md`

**Audited predecessor commit:**  
`4931e4daa124587a789ac27b841f499295facf5e`

**Repair scope:** trusted certificate boundary, provenance, validation, and repository hygiene only.

**Mathematical non-regression rule:** the independently audited ASTs of B1–B8, A8,
C10–C12 and the registered 11.01–11.03 definition ASTs are regression-locked.

---

## 1. Overall repair result

The first foundational audit did **not** require replacement of any stored
primitive schema AST or normalized S1–S5 basis.

M0.3 repairs the trusted-certificate boundary and all associated P0/P1 defects.

The repaired candidate remains **not frozen** until the focused closure audit
certifies the exact new commit.

---

## 2. P0-01 — definition conversion / `equiv_s`

### Defect

The predecessor specification permitted optional/silent definition elaboration
and did not uniquely determine how visible use of 11.01–11.03 is certified.

### Repair

M0.3 adopts one normative mechanism:

```text
definition_conversion
```

This is a trusted metalinguistic certificate kind, **not** a fifth Lewis
inference rule.

Every conversion records:

```text
parents: [<node-id>]
definition_id
direction
occurrence_path
```

with:

```text
direction ∈ {expand, contract}
```

The checker must:

1. resolve the registered definition;
2. traverse exactly one surface occurrence;
3. match one side with a single consistent metavariable environment;
4. instantiate the opposite side with the same environment;
5. replace exactly that occurrence;
6. require exact surface-AST equality with the declared conclusion.

No second or implicit conversion is permitted.

### Surface identity rule

All Lewis primitive operations use exact visible/surface AST identity.

Full definitional erasure is diagnostic only.

---

## 3. P1-01 — `postulate_instance` versus `Sa`

### Defect

The predecessor did not separate schema instantiation from object-level Lewis
substitution precisely enough.

### Repair

`postulate_instance`:

- parentless;
- uses schema metavariables `P,Q,R,...`;
- map domain is exactly the metavariable set of the selected registered schema;
- values are object formulas;
- extra or missing keys are rejected;
- schema admission is checked against the exact proof `basis_id`.

`Sa`:

- has exactly one checked parent theorem;
- acts only on object atom names;
- substitution is simultaneous, one-pass, and nonrecursive into replacement values;
- unmentioned atoms are fixed;
- keys not occurring in the parent are rejected;
- no definition conversion is performed implicitly.

The two namespaces are disjoint.

---

## 4. P1-02 — occurrence-path grammar

M0.3 freezes one grammar shared by `Sb` and `definition_conversion`.

Logical payload:

```yaml
[]
[arg]
[left]
[right]
[right, arg]
```

Only `arg`, `left`, and `right` are legal segments.

The atom payload `name` is not traversable.

Dotted notation such as `.right.arg` is renderer-only.

Exactly one occurrence is selected per primitive `Sb` or
`definition_conversion` node.

---

## 5. P1-03 — exact S5 basis identity

Every proof now declares:

```text
system
basis_id
```

Stable basis IDs:

```text
S1_B1_B7
S2_B1_B8
S3_B1_B7_A8
S4_B1_B7_C10
S5_PRIMARY_B1_B7_C11
S5_ALT_B1_B7_C10_C12
```

For S5 the two bases are separate.

The checker must never admit the union:

```text
B1–B7 + C10 + C11 + C12
```

as one primitive basis.

Future bridge proofs declare:

```text
source_basis_id
target_basis_id
```

and expand to target-basis native certificates.

---

## 6. P2 source/provenance repairs

### Parry 1939

The source register no longer says Parry literally prints all of 11.1–11.7 as
primitive.

It now records the reduced displayed list and the role of McKinsey's derivation
of 11.5.

### L&L p. 498

The C10/C11/C12 source entries now preserve the paragraph's explicit
A1–A8/B1–B9 background qualification.

### L&L p. 501

The source register and system spec explicitly use p. 501 as the canonical
direct source for the two B1–B7-based S5 presentations.

---

## 7. P2 obligation-register repair

The stale states `blocked`, `open`, and `repair_needed` have been replaced for
implemented first-audit repairs by:

```text
repair_implemented_reaudit_pending
```

This status means:

> the repair exists and passes local validation, but is not independently
> certified until the focused closure audit succeeds.

---

## 8. P2 freeze-readiness validation

`validate_spec.py --freeze` now checks, among other things:

- spec version/status consistency;
- exact AST registry;
- definition well-formedness;
- no implicit definition conversion;
- exact certificate-kind vocabulary;
- Sa/schema-instantiation namespace separation;
- occurrence-path grammar;
- stable basis IDs;
- S5 anti-union policy;
- audited AST fingerprints.

`validate_source_register.py --freeze` checks:

- source-register/spec coverage;
- exact Parry provenance qualification;
- p. 498 / p. 501 S5 provenance;
- closure-repair obligation coverage;
- absence of unresolved `blocked`, `open`, or `repair_needed` statuses;
- existence of registered source files in the real repository.

These validators are still structural/provenance safeguards, not replacements
for independent mathematical audit.

---

## 9. P2 CI coverage

The M0 GitHub Actions workflow now triggers on:

```text
AGENTS.md
README.md
CONTRIBUTING.md
docs/**
spec/**
audit/m0/**
scripts/**
tests/spec/**
tests/conftest.py
pyproject.toml
```

CI also runs both normal and `--freeze` validator modes.

---

## 10. P2 repository hygiene

The package includes:

```text
scripts/apply_m0_v0_3_cleanup.sh
```

It:

- archives/removes the superseded active `FOUNDATIONAL_SPEC_v0.2.md`;
- removes materialized `*:Zone.Identifier` files.

CI rejects tracked `*:Zone.Identifier`.

---

## 11. P3 improvements adopted

### Explicit atom status

`atom` is explicitly marked primitive in `language.yaml`.

### Ambiguous ASCII fishhook alias

The risky `=>` input alias is removed.

Users can still input the fishhook via the dedicated project aliases.

---

## 12. Formula-level non-regression

`audit/m0/certified_ast_fingerprints.yaml` locks:

- B1–B8;
- A8;
- C10–C12;
- DEF_OR;
- DEF_STRICT_IMP;
- DEF_EQUIV_S.

These fingerprints are computed from canonicalized AST data.

`validate_spec.py --freeze` fails if a locked AST changes.

This lock does not itself prove source correctness; it prevents accidental
regression from the formula layer already independently audited.

---

## 13. Files intentionally superseded

The active foundational specification is now:

```text
docs/FOUNDATIONAL_SPEC_v0.3.md
```

The previous v0.2 is retained only under:

```text
docs/archive/FOUNDATIONAL_SPEC_v0.2.md
```

---

## 14. M1 gate

M1 implementation remains forbidden.

Next step:

1. upload this repair package;
2. run all validators/tests;
3. record the exact candidate commit;
4. run the focused Work Max closure recheck;
5. proceed to M1 only if the first-line verdict is:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
