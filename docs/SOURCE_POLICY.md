# Source Policy

## 1. Canonical authority

For the S1–S5 core, the canonical historical authority is:

**C. I. Lewis and C. H. Langford, _Symbolic Logic_, 2nd edition, 1932.**

The supplied Dover/1959 reprint may be used as the working scan where pagination reproduces the 1932 edition.

The relevant material includes Chapter VI and Appendix II.

## 2. Secondary sources

Secondary sources may be used for reconstruction, cross-checking, proof discovery, historical notes, alternative bases, and derived rules.

Priority working sources include:

- Robert Feys, _Modal Logics_;
- W. T. Parry (1939);
- J. C. C. McKinsey;
- Hughes/Cresswell material on strict implication;
- Lewis (1918), for historical comparison;
- later historical and technical literature where needed.

These sources do **not** override the normalized L&L specification without an explicit foundational revision.

## 3. Historical notation versus prover notation

The prover follows L&L in logical content, not in every typographical convention.

Important normalization decisions:

- L&L historical `=` for logical/strict equivalence is not used as the object-language symbol;
- the prover uses `equiv_s` / `\equiv_s`;
- strict implication retains the fishhook;
- `Box` is not part of the M0 object language;
- schema/metalevel equality remains distinct from all object-language connectives.

A source transcription must therefore record both:

```text
historical_form
```

and:

```text
normalized_ast
```

where necessary.

## 4. Provenance requirement

Every primitive schema must eventually record enough provenance to support human rechecking:

- work;
- edition/year;
- chapter/appendix;
- printed page;
- historical label;
- optional scan filename;
- optional transcription note.

Every imported derived theorem should additionally record:

- source theorem/rule number if available;
- claimed source system;
- normalized target formula;
- checked native proof certificate.

## 5. Source hierarchy under disagreement

If sources disagree:

1. do not silently choose;
2. record the disagreement;
3. prefer L&L 1932 for the canonical historical definition of S1–S5;
4. determine whether the disagreement is merely notation, a different equivalent basis, a later strengthening, or an actual mathematical conflict;
5. update the normalized specification only through an explicit foundational change.

## 6. No authority by citation alone

A theorem is not trusted by the kernel because a book or article states it.

Secondary literature may seed a theorem library only after a certificate has been checked against the target normalized basis.

## 7. Reference files

The `Strict_Implication/` directory is a research/reference corpus.

It is not executable specification.

No implementation should parse a PDF at runtime to determine what the calculus is. The executable source of truth is `spec/*.yaml`, after audit.


## 8. Project rule labels

`Sa`, `Sb`, `Ad`, and `Smp` are stable project/editorial labels used by this
repository and the associated manuscript. They must not be described as
literal symbolic labels printed by Lewis & Langford.

Canonical L&L provenance is:

- `Sa`: Substitution (b), p. 125;
- `Sb`: Substitution (a), p. 125;
- `Ad`: Adjunction, p. 126;
- `Smp`: Inference, p. 126.
