# Lewis S1–S5 Native Syntactic Prover
## Foundational specification v0.3

**Status:** M0 closure-audit candidate  
**Canonical historical source:** Lewis & Langford, *Symbolic Logic* (1932)  
**Executable logical specification:** `spec/*.yaml`

---

## 1. Purpose

The project produces machine-checkable Hilbert-style proofs in Lewis's strict
implication systems S1–S5.

The accepted theorem certificate must be native to the selected normalized
Lewis basis.

Modern search is permitted only outside the trusted boundary.

\[
\boxed{\text{modern search may discover; the native checker alone certifies}}
\]

---

## 2. Object language and project normalization

The project follows L&L in logical content but deliberately disambiguates
notation.

### Primitive/core formula constructors

```text
atom
neg
and
poss
```

### First-class defined surface constructors

```text
or
strict_imp
equiv_s
```

The fishhook remains visible for `strict_imp`.

L&L's overloaded object-language `=` is not reproduced. Strict equivalence is
represented by `equiv_s` / `\equiv_s`.

Metalanguage equality and definitional equality remain separate.

`\Box` is not part of M0.

B9 and propositional-existence machinery are not part of M0.

---

## 3. Registered definitions

The project normalizes L&L 11.01–11.03 as:

```text
DEF_OR:
P ∨ Q := ∼(∼P ∧ ∼Q)

DEF_STRICT_IMP:
P ⥽ Q := ∼◇(P ∧ ∼Q)

DEF_EQUIV_S:
P ≡ₛ Q := (P ⥽ Q) ∧ (Q ⥽ P)
```

These are metalinguistic definitions, not additional Lewis inference rules.

### Frozen definition policy

There is **no implicit definition elaboration** in primitive-rule checking.

Any visible expansion or contraction is represented by an explicit trusted
`definition_conversion` certificate node.

All Lewis primitive-rule matching is exact on the visible surface AST.

A separate deterministic full-erasure function exists only for specification
checking and diagnostic rendering.

---

## 4. Primitive Lewis operations

M0 contains exactly four Lewis operations:

```text
Sa
Sb
Ad
Smp
```

These are project labels for:

- `Sa`: L&L Substitution (b), uniform substitution;
- `Sb`: L&L Substitution (a), substitution of equivalents;
- `Ad`: Adjunction;
- `Smp`: L&L Inference / strict detachment.

`definition_conversion` is trusted certificate checking but is not a fifth
Lewis inference rule.

No unrestricted necessitation is admitted.

---

## 5. Postulate instances versus Sa

A primitive schema instance and `Sa` are different syntactic operations.

### Postulate instance

Maps schema metavariables:

```text
P,Q,R,...
```

to object formulas.

It is parentless and is admitted only when the schema belongs to the selected
`basis_id`.

### Sa

Acts on object atom names in an already certified theorem.

It is simultaneous, one-pass, and nonrecursive.

Schema metavariables and object atoms are disjoint namespaces.

---

## 6. Normalized system bases

The project uses:

```text
S1 = B1–B7
S2 = B1–B8
S3 = B1–B7 + A8
S4 = B1–B7 + C10
```

S5 has two separately identified bases:

```text
S5_PRIMARY_B1_B7_C11
  = B1–B7 + C11

S5_ALT_B1_B7_C10_C12
  = B1–B7 + C10 + C12
```

Every proof certificate declares a stable `basis_id`.

The two S5 bases are never unioned.

---

## 7. A-series normalization and S3

L&L historically presents S3 by A1–A8.

The executable prover does not store a second A1–A7 primitive list.

This is not the false claim that A1–A6 are all literal B1–B6 copies.

The precise classification verified in the foundational audit is:

```text
A1 = literal B1
A2 = S1 theorem, nonliteral
A3 = literal B3
A4 = S1 theorem, nonliteral
A5 = literal B5
A6 = literal B6
A7 = S1 theorem
A8 = additional S3 principle
```

Parry 1939 pp. 137–138 provides direct syntactic support for the normalized
B1–B7+A8 presentation. Parry's displayed reduced postulate list omits 11.5
because McKinsey had shown it derivable; the project retains B5 because the
chosen normalized S1 basis is L&L B1–B7.

Future historical bridge certificates remain a proof-library obligation, not
additional M0 primitives.

---

## 8. Stored primitive schemas

The executable primitive schema registry is exactly:

```text
B1 B2 B3 B4 B5 B6 B7 B8 A8 C10 C11 C12
```

Their ASTs were independently source-checked in the 2026-09-04 foundational
audit and are regression-locked by:

```text
audit/m0/certified_ast_fingerprints.yaml
```

Any AST fingerprint change is a foundational change requiring source re-audit.

---

## 9. C10/C11/C12 provenance

L&L p. 498 gives the derivability relations among C10, C11, C12 under that
paragraph's stated A1–A8/B1–B9 background.

L&L p. 501 canonically states the two B1–B7-based presentations of S5.

The source register records both facts.

Neither historical statement is itself a machine proof certificate.

Future native bridge certificates must establish the relevant target-basis
derivations.

---

## 10. Occurrence paths

`Sb` and `definition_conversion` use one normative structural path grammar:

```text
[]                  root
[arg]
[left]
[right]
[right,arg]
...
```

Only `arg`, `left`, and `right` are logical path segments.

The atom payload `name` is never traversable.

Dotted forms are renderer-only.

Defined first-class nodes are traversed as visible surface nodes.

---

## 11. Trusted certificate boundary

The normative certificate kinds are exactly:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Detailed contracts are in `docs/PROOF_CERTIFICATE_SPEC.md` and
`spec/rules.yaml`.

Derived theorem and bridge macros are outside the trusted kernel vocabulary and
must expand before checking.

---

## 12. Surface proof versus erased diagnostic form

A primitive proof may still display the fishhook and `equiv_s`.

"Primitive proof" concerns proof operations, not forced elimination of all
defined notation.

A separate fully erased diagnostic formula view may reduce formulas to:

```text
atom
neg
and
poss
```

This is not the ordinary user proof display.

---

## 13. Search failure

Until a separately certified decision procedure exists:

```text
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
```

is permitted.

Search exhaustion alone never licenses:

```text
NOT_A_THEOREM
```

---

## 14. Freeze discipline

The M0 candidate is ready for closure audit only when:

- structural spec validation passes;
- source-register validation passes;
- freeze-readiness validation passes;
- AST fingerprints match the independently audited formula layer;
- no P0/P1 repair obligation remains unresolved;
- CI passes on the exact candidate commit;
- tracked Windows metadata is absent.

M0 becomes frozen only if the focused independent closure audit certifies the
exact candidate commit.

Only then may M1 trusted-kernel implementation begin.
