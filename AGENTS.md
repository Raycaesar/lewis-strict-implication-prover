# AGENTS.md

## Scope

This repository implements a native syntactic prover for Lewis strict-implication systems S1–S5.

This file is binding on Codex and other coding agents working in the repository.

## 1. Source of truth

Before changing any logic-sensitive code, read in this order:

1. `docs/FOUNDATIONAL_SPEC_v0.2.md`
2. `docs/SOURCE_POLICY.md`
3. `spec/language.yaml`
4. `spec/rules.yaml`
5. `spec/schemas.yaml`
6. `spec/systems.yaml`
7. `docs/PROOF_CERTIFICATE_SPEC.md`
8. `docs/ARCHITECTURE.md`

If prose documentation conflicts with `spec/*.yaml`, **stop and report the conflict**. Do not guess which version is intended.

No agent may silently edit the calculus to make implementation easier.

## 2. Trusted-kernel principle

The final proof checker is the trusted component.

Every accepted theorem certificate must ultimately expand to:

- a declared primitive axiom-schema instance of the selected system;
- uniform substitution (`Sa`);
- replacement of strict equivalents (`Sb`);
- adjunction (`Ad`);
- strict detachment (`Smp`);
- explicitly licensed definition expansion/contraction, if and only if the specification permits it in the relevant mode.

Derived rules, theorem-library entries, bridge lemmas, heuristics, semantic checks, SAT encodings, tableaux, sequent systems, or external provers must never be accepted as primitive proof steps.

## 3. Forbidden shortcuts

Unless the specification is deliberately revised and re-audited, do not introduce:

- unrestricted necessitation;
- Kripke-semantic validity as a proof step;
- matrix validity as a proof step;
- tableau or sequent rules as proof steps;
- modern K/T/S4/S5 Hilbert axioms as substitutes for the Lewis bases;
- object-language `=` for strict equivalence;
- `Box` as a primitive or default object-language operator;
- B9 or propositional existential quantification into the initial core.

Search may consult untrusted auxiliary procedures, but the result is accepted only after reconstruction and kernel verification.

## 4. Notation invariants

- Preserve the strict-implication fishhook in rendering.
- Internal node name: `strict_imp`.
- Strict equivalence is represented internally by `equiv_s`.
- Metalanguage equality/definition must never be parsed as object-language strict equivalence.
- The core M0 language does not contain `Box`.
- Keep historical labels (`B1`, `B8`, `A8`, `C10`, `C11`, `C12`) stable.

## 5. System invariants

Normalized prover bases:

- S1: B1–B7
- S2: B1–B8
- S3: B1–B7 + A8
- S4: B1–B7 + C10
- S5: B1–B7 + C11

Do not duplicate A1–A6 as independent stored schemas merely because the 1932 historical presentation lists an A-series.

A7 is not primitive in the normalized prover. It belongs in the derived/historical proof corpus once a checked S1 proof is available.

The alternative S5 basis S1 + C10 + C12 is not automatically trusted. Its equivalence to the primary S5 basis must be represented by checked bridge proofs.

## 6. Implementation stages

Do not skip stages:

- M0: specification normalization and audit
- M1: tiny trusted kernel
- M2: historical regression corpus
- M3: certified derived-rule library
- M4: automatic proof search
- M5: system bridge library
- M6: user interface

A coding task must state which milestone it belongs to.

## 7. Proof-search failure

Never infer non-theoremhood merely because bounded search fails.

Allowed status:

`NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS`

Not allowed without a separately certified decision procedure:

`NOT_A_THEOREM`

## 8. Testing discipline

Every logic-sensitive feature requires:

1. positive tests;
2. malformed-certificate rejection tests;
3. wrong-system rejection tests where relevant;
4. a primitive-only expansion test for any derived macro;
5. regression tests preserving historical theorem labels and provenance.

## 9. Change control

Any change to:

- the object language;
- primitive rules;
- primitive system bases;
- schema ASTs;
- definition status of a connective;
- interpretation of `equiv_s`;
- certificate semantics;

is a **foundational change**.

Foundational changes must not be bundled into ordinary refactors. They require an explicit specification update and a fresh foundational audit.

## 10. Coding style

When implementation begins:

- prefer small pure functions in the kernel;
- use immutable/hashable formula nodes where practical;
- keep parser/rendering separate from proof validity;
- keep search untrusted and outside the kernel;
- make certificate errors structured and deterministic;
- do not let convenience APIs bypass kernel checking.
