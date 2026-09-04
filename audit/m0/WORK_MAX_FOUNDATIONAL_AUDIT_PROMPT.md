# Work Max — from-scratch M0 foundational audit of the Lewis S1–S5 native syntactic prover

Execute this audit now.

Repository:

`Raycaesar/lewis-strict-implication-prover`

This is a **read-only foundational audit**. Do not implement the prover, do not
write M1 kernel code, and do not silently repair files while auditing.

The purpose is to decide whether the M0 formal specification is sufficiently
correct, source-faithful, precise, and internally coherent to be frozen and
used as the immutable logical basis for the trusted proof checker.

## Required first-line verdict

The first line of the report must be exactly one of:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

or

```text
M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED
```

No intermediate verdict.

## Read in this order

1. `AGENTS.md`
2. `README.md`
3. `docs/SOURCE_POLICY.md`
4. `docs/FOUNDATIONAL_SPEC_v0.2.md`
5. `docs/ARCHITECTURE.md`
6. `docs/PROOF_CERTIFICATE_SPEC.md`
7. `docs/ROADMAP.md`
8. `spec/README.md`
9. `spec/language.yaml`
10. `spec/rules.yaml`
11. `spec/schemas.yaml`
12. `spec/systems.yaml`
13. `audit/m0/source_register.yaml`
14. `audit/m0/foundational_obligations.yaml`
15. `audit/m0/FIRST_PASS_FINDINGS.md`
16. `audit/m0/FREEZE_CHECKLIST.md`
17. the relevant primary and secondary sources in `Strict_Implication/`.

## Canonical source policy

For the native calculus, Lewis & Langford, *Symbolic Logic*, 2nd ed. 1932
(the supplied Dover reprint) is canonical.

At minimum inspect directly:

- p. 123: primitive ideas and 11.01;
- p. 124: 11.02, 11.03, 11.1;
- p. 125: 11.2–11.7 and Substitution clauses (a), (b);
- p. 126: Adjunction and Inference;
- p. 493: A1–A8 and B1–B9;
- p. 497: C10–C13 and C10.1;
- p. 498: relations (12)–(14) among C10, C11, C12;
- p. 499: continuation of the C10/C11/C12 equivalence discussion;
- pp. 500–501: explicit descriptions of S1–S5.

Use Parry 1939 pp. 137–138 as a major syntactic cross-check for the normalized
S3 presentation.

Use Feys for proof-rule and derived-rule cross-checks, but never let Feys
override the canonical L&L system without explicit justification.

Hughes/Cresswell is a modern cross-check only.

Lewis 1918 is historical reference only.

## Project normalization constraints to respect

The audit must not reject the project merely for not reproducing L&L
typography.

The intended normalization is:

- preserve the Lewis fishhook as strict implication;
- use `equiv_s` / `\equiv_s` rather than L&L object-language `=`;
- keep object language and metalanguage equality distinct;
- do not add Box to the M0 native object language;
- exclude B9 from the initial propositional/modal S1–S5 core;
- avoid redundant executable copies of the A-series where the normalized basis
  already recovers them;
- use S1+A8 as the normalized S3 basis only if this is adequately source-
  justified and mathematically safe.

## Mandatory audit questions

### 1. Language and definitions

Verify independently:

- primitive/core constructors;
- DEF_OR / 11.01;
- DEF_STRICT_IMP / 11.02;
- DEF_EQUIV_S / 11.03;
- exact separation of object-language `equiv_s` from metalanguage equality;
- whether the current first-class defined-node architecture is coherent.

Most importantly, resolve this question:

> L&L list logical equivalence among the primitive ideas, but also give 11.03.
> Is the project's treatment of `equiv_s` as a first-class normalized
> object-language connective with definitional expansion/contraction faithful
> enough for a trusted syntactic checker?

Do not hand-wave this point.

### 2. Primitive rules

Check the exact rules/operations against pp. 125–126.

Confirm or reject:

- Sa = project label for uniform Substitution clause (b);
- Sb = project label for substitution/replacement of equivalents clause (a);
- Ad = project label for Adjunction;
- Smp = project label for L&L Inference.

Check that B7 is not confused with the metalevel Inference operation.

Check that no hidden necessitation or modern modal rule has entered the core.

### 3. Schema transcription

For B1–B8, A8, C10, C11, C12:

- check every connective;
- check every negation;
- check grouping/parenthesization;
- check which formulas are strict implications versus conjunctions of strict
  implications;
- compare the YAML AST, display string, and primary source.

Treat C10–C12 as high-risk because a single negation error changes the system.

### 4. A-series normalization

Audit the decision not to store A1–A7 separately.

Do not accept the false shortcut that A1–A6 are all literal formula-for-formula
copies of B1–B6.

Determine precisely:

- which are literal matches;
- which are S1 consequences;
- whether Parry 1939 adequately supports the S1+A8 normalized S3 basis;
- what future bridge certificates are required.

### 5. S1–S5 system bases

Independently verify:

- S1 B1–B7;
- S2 B1–B8;
- historical S3 A1–A8 and normalized S3 S1+A8;
- S4 B1–B7+C10;
- S5 B1–B7+C11;
- S5 alternative B1–B7+C10+C12.

Check that theorem inclusion is never implemented as unproved primitive-basis
inheritance.

### 6. C10/C11/C12 bridge architecture

Verify the source claims at L&L p. 498:

- C11 ⊢ C10;
- C11 ⊢ C12;
- C10+C12 ⊢ C11.

Check that the future proof library must still carry native certificates even
though the historical source states these results.

### 7. Definition conversion and proof certificates

The present architecture insists that definitions are not new inference rules.

Determine a precise acceptable certificate mechanism for visible "by
definition" proof transformations.

Audit whether:

- a trusted metalinguistic `definition_conversion` node is appropriate;
- it must record definition ID, direction, parent, and occurrence path;
- primitive-only rendering remains faithful;
- it interacts safely with Sb.

This is a freeze-critical issue.

### 8. Validator adequacy

Run or inspect:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
pytest
```

Determine what these validators establish and, equally importantly, what they
do **not** establish.

Do not treat CI success as proof that the calculus is mathematically correct.

## Defect classification

Use:

- **P0** — foundational blocker; M0 cannot be frozen.
- **P1** — major specification/math/source defect requiring repair before M1.
- **P2** — local clarification/provenance/test defect.
- **P3** — optional improvement.

For every P0/P1 give:

1. exact file/location;
2. exact defect;
3. why it matters;
4. required repair;
5. whether it changes the intended calculus;
6. re-audit dependency.

## Required report sections

1. Overall verdict.
2. Executive summary.
3. Source-by-source audit.
4. Language/definition audit.
5. Primitive-rule audit.
6. Schema-by-schema audit table.
7. S1–S5 basis audit.
8. Normalized S3 audit.
9. S5 bridge audit.
10. Proof-certificate/definition-conversion audit.
11. Validator/CI audit.
12. Full P0–P3 defect register.
13. Exact freeze checklist status.
14. Minimal repair plan if not certified.
15. Final recommendation: whether M1 trusted-kernel implementation may begin.

## Anti-shortcut instructions

- Do not use Kripke semantics or modern normal-modal equivalence as a substitute
  for checking the native calculus.
- Do not assume prior ChatGPT analyses are correct.
- Do not certify because the repository is tidy or CI is green.
- Do not manufacture objections merely to avoid certification.
- Do not require restoration of L&L's overloaded object-language `=` if the
  normalized `equiv_s` treatment is mathematically and proof-theoretically
  sound.
- Do not require Box notation.
- Do not require B9.
- Do not write implementation code.

Return one detailed Markdown report.
