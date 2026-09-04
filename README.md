# Lewis S1–S5 Native Syntactic Prover

A historically controlled, machine-checkable theorem prover for the Lewis systems of strict implication **S1–S5**, normalized from Lewis & Langford (1932).

The project has one overriding requirement:

> **Search may be modern; every accepted proof certificate must compile down to a proof licensed by the selected Lewis system.**

The final user-facing prover is intended to let a user:

1. choose **S1, S2, S3, S4, or S5**;
2. enter a formula in strict-implication notation;
3. obtain a line-by-line Hilbert-style syntactic proof;
4. inspect the exact justification for every line;
5. optionally expand every derived rule or stored theorem back to the trusted primitive basis.

## Current status

The project is in the **M0 specification stage**. No automatic prover implementation is trusted yet.

The executable logical specification currently lives in:

```text
spec/
├── language.yaml
├── rules.yaml
├── schemas.yaml
└── systems.yaml
```

The governing historical and architectural documents live in `docs/`.

## Canonical notation

The project deliberately does **not** reproduce every typographical convention of Lewis & Langford.

- strict implication keeps the Lewis **fishhook** as the characteristic connective;
- strict equivalence is represented as `equiv_s` / `\equiv_s`, not by object-language `=`;
- object language and metalanguage must remain formally distinct;
- `\Box` is not part of the M0 language, because it is not part of the chosen L&L presentation;
- B9 and propositional-existence machinery are excluded from the initial S1–S5 propositional core.

## Normalized prover bases

The machine-oriented bases are:

| System | Normalized basis |
| --- | --- |
| S1 | B1–B7 |
| S2 | B1–B8 |
| S3 | B1–B7 + A8 |
| S4 | B1–B7 + C10 |
| S5 | B1–B7 + C11 |

A1–A6 are not duplicated because they coincide with B1–B6 in the relevant normalized presentation. A7 is treated as an S1-derived theorem rather than a primitive schema. The alternative S5 basis `S1 + C10 + C12` is to be admitted only through a checked bridge certificate.

## Primitive proof operations

The trusted core recognizes only the primitive operations encoded in `spec/rules.yaml`:

- uniform substitution (`Sa`);
- replacement of strict equivalents (`Sb`);
- adjunction (`Ad`);
- strict detachment / strict modus ponens (`Smp`).

No unrestricted necessitation is part of the M0 trusted core.

## Repository map

```text
.
├── AGENTS.md
├── CONTRIBUTING.md
├── README.md
├── Strict_Implication/        # historical/reference literature
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FOUNDATIONAL_SPEC_v0.2.md
│   ├── PROOF_CERTIFICATE_SPEC.md
│   ├── ROADMAP.md
│   └── SOURCE_POLICY.md
├── proofs/
│   ├── README.md
│   └── bridges/
│       └── README.md
├── spec/
│   ├── language.yaml
│   ├── rules.yaml
│   ├── schemas.yaml
│   └── systems.yaml
└── tests/
    ├── fixtures/
    │   └── README.md
    └── historical/
        └── README.md
```

## Development rule

Do **not** implement proof search until the M0 specification has passed a separate foundational audit.

See:

- `docs/FOUNDATIONAL_SPEC_v0.2.md`
- `docs/ROADMAP.md`
- `AGENTS.md`

## Historical source

The canonical source for the definition of the systems is:

C. I. Lewis and C. H. Langford, *Symbolic Logic*, 2nd ed., 1932.

Later sources such as Feys, Parry, McKinsey, and Hughes/Cresswell are used for derived rules, proof reconstruction, alternative axiomatizations, and search guidance, but they do not silently override the normalized L&L core.
