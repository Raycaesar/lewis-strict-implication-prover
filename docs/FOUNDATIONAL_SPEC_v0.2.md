# Lewis S1–S5 Native Syntactic Prover
## Foundational specification v0.2

**Status:** M0 working specification, not yet frozen  
**Canonical historical source:** Lewis & Langford, *Symbolic Logic* (1932)  
**Executable specification:** `spec/*.yaml`

---

## 1. Purpose

The prover is designed to produce Hilbert-style syntactic proofs in the Lewis systems of strict implication S1–S5.

The central correctness criterion is not merely that a target formula be valid or derivable in some equivalent modern modal logic. The program must provide a certificate whose steps are licensed by the selected Lewis system, after expansion of all derived conveniences.

\[
\boxed{\text{modern search is allowed; native Lewis certificates are required}}
\]

---

## 2. Normalization policy

The implementation is historically based on Lewis & Langford (1932), but it is **not a diplomatic transcription of 1932 typography**.

We deliberately normalize the representation where necessary to prevent object-language / metalanguage confusion and to support exact machine checking.

### 2.1 Strict implication

Strict implication remains the characteristic **fishhook** connective in rendering.

Internal constructor:

```text
strict_imp(A, B)
```

Recommended LaTeX rendering:

```text
A \strictif B
```

The exact renderer macro may be configured, but it must remain visibly distinct from material implication.

### 2.2 Strict equivalence

Lewis & Langford use `=` in a way that is unacceptable as a machine-level object-language notation because it risks collision with metalanguage equality and definitional equality.

The prover therefore uses:

```text
equiv_s(A, B)
```

rendered as:

```text
A \equiv_s B
```

Any use of ordinary `=` in source documentation is historical notation only.

### 2.3 No Box in the M0 core

The M0 object language does not introduce `Box`.

Necessity may later be defined or rendered in a derived presentation, but it is not a core AST constructor or primitive input symbol at this stage.

### 2.4 Possibility

Possibility remains represented by the Lewis diamond notation, with internal constructor:

```text
poss(A)
```

and LaTeX form based on `\poss`.

### 2.5 Metalanguage

Schema metavariables, AST equality, rewrite paths, definitions, and proof dependencies belong to the metalanguage. They must not be encoded by object-language connectives.

---

## 3. Primitive proof operations

The initial trusted kernel recognizes the four proof operations specified in `spec/rules.yaml`:

- `Sa` — uniform substitution;
- `Sb` — replacement of strict equivalents;
- `Ad` — adjunction;
- `Smp` — strict detachment.

No unrestricted necessitation rule is primitive.

A later derived rule may be implemented as a macro only after it possesses a checked expansion into the trusted primitives.

---

## 4. Normalized S1–S5 bases

For the prover, the following compact bases are used.

### S1

```text
B1, B2, B3, B4, B5, B6, B7
```

### S2

```text
S1 + B8
```

### S3

```text
S1 + A8
```

This is a normalized machine basis.

Lewis & Langford historically present S3 through A1–A8. We do not duplicate A1–A6 because they agree with the corresponding B-series principles in the relevant normalized presentation, and A7 is to be stored as an S1-derived theorem after its proof is kernel-checked.

### S4

```text
S1 + C10
```

### S5

Primary normalized basis:

```text
S1 + C11
```

Alternative historical/certified basis:

```text
S1 + C10 + C12
```

The latter must not be treated as equivalent by configuration alone. Equivalence must be backed by explicit bridge certificates.

---

## 5. Non-core B9

B9, the Existence Postulate, is excluded from the initial propositional S1–S5 prover.

Reasons:

1. it introduces additional propositional-existence machinery;
2. it is not needed for ordinary strict-implication theorem proving;
3. including it would enlarge the parser, AST, substitution discipline, and proof kernel before the propositional core is stable.

Any future B9 extension must be a separate milestone.

---

## 6. A-series normalization

The repository does not store redundant independent copies of A1–A6.

A7 is not primitive in the normalized prover.

A8 remains stored because it supplies the characteristic additional S3 principle in the normalized basis.

Historical source records may still mention A1–A8, but executable `spec/*.yaml` must keep a clear distinction between:

- historical presentation;
- normalized machine basis;
- derived theorem;
- certified alternative basis.

---

## 7. System inclusion versus primitive basis

The theorem hierarchy S1–S5 must not be confused with literal inheritance of primitive axiom lists.

The prover shall represent separately:

```text
primitive_basis(Sn)
```

and:

```text
certified_theorem_inclusion(Si, Sj)
```

A theorem proved under one basis may be reused under another only when the required bridge is itself certified or when the theorem is independently reproved in the target basis.

---

## 8. Definitions and abbreviations

A connective may be:

1. primitive;
2. defined;
3. parser sugar;
4. renderer sugar.

These statuses must be explicitly encoded.

The trusted kernel must not silently treat parser sugar as a new proof rule.

In primitive-only proof output, any step depending on a defined connective must be expandable according to the formal definition policy eventually frozen in the specification.

---

## 9. Proof objects

Internally, a proof is a DAG.

Each node must identify:

- conclusion formula;
- justification kind;
- parent proof nodes;
- axiom/schema identifier if applicable;
- substitution map if applicable;
- replacement direction/path if applicable;
- provenance metadata when it is a stored theorem or macro.

The printed Hilbert proof is a deterministic linearization of this DAG.

See `docs/PROOF_CERTIFICATE_SPEC.md`.

---

## 10. Trusted versus untrusted components

### Trusted

- formula structural validation;
- schema-instance checking;
- substitution checking;
- strict-equivalence replacement checking;
- adjunction;
- strict detachment;
- proof-DAG dependency verification;
- declared definition expansion/contraction checks.

### Untrusted

- heuristic theorem lookup;
- forward search;
- backward search;
- bidirectional search;
- proof ranking;
- semantic filters;
- external provers;
- learned heuristics.

An untrusted component may suggest a proof. Only the trusted kernel may accept it.

---

## 11. Failure statuses

Before a separate syntactic decision procedure is certified, bounded proof-search failure means only:

```text
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
```

It does not mean:

```text
NOT_A_THEOREM
```

---

## 12. M0 exit criterion

M0 is complete only when:

1. `spec/language.yaml` is audited;
2. `spec/rules.yaml` is audited;
3. `spec/schemas.yaml` is audited formula-by-formula;
4. `spec/systems.yaml` is audited;
5. all notation decisions are internally consistent;
6. source provenance is sufficient to reconstruct each primitive schema;
7. a fresh foundational audit finds no unresolved calculus-level ambiguity.

Only then is the specification marked **M0 FROZEN** and M1 kernel implementation begins.
