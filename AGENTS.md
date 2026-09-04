# AGENTS.md

## Scope

This repository implements a native syntactic prover for Lewis strict-implication systems S1–S5.

This file is binding on Codex and other coding agents.

## 1. Current milestone

The repository is an **M0.3 closure-audit candidate**.

Do not implement M1 trusted-kernel code until the exact candidate commit has received:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```

## 2. Source of truth

Before changing logic-sensitive material, read in this order:

1. `docs/FOUNDATIONAL_SPEC_v0.3.md`
2. `docs/SOURCE_POLICY.md`
3. `spec/language.yaml`
4. `spec/rules.yaml`
5. `spec/schemas.yaml`
6. `spec/systems.yaml`
7. `docs/PROOF_CERTIFICATE_SPEC.md`
8. `docs/ARCHITECTURE.md`
9. `audit/m0/source_register.yaml`
10. `audit/m0/foundational_obligations.yaml`
11. `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.3.md`

If executable YAML and normative prose disagree, stop and report the conflict. Do not guess.

## 3. Trusted-kernel invariant

Every accepted theorem certificate must reduce to exactly these trusted certificate kinds:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Only `Sa`, `Sb`, `Ad`, and `Smp` are Lewis inference operations.

`definition_conversion` is trusted metalinguistic checking of registered definitions and is **not** a fifth Lewis inference rule.

## 4. Exact surface-AST rule matching

All Lewis primitive rules operate on exact visible/surface ASTs.

Do not silently expand or contract:

```text
or
strict_imp
equiv_s
```

to make a rule application succeed.

Visible definitional change requires an explicit `definition_conversion` node.

## 5. Namespace separation

Never conflate:

- schema metavariables `P,Q,R,...`;
- object atoms `p,q,r,...`;
- object-language `equiv_s`;
- metalanguage structural equality;
- metalanguage `:=`.

`postulate_instance` maps schema metavariables to object formulas.

`Sa` acts only on object atom names in an already checked theorem.

## 6. Basis discipline

Every proof certificate declares `system` and `basis_id`.

Stable basis IDs:

```text
S1_B1_B7
S2_B1_B8
S3_B1_B7_A8
S4_B1_B7_C10
S5_PRIMARY_B1_B7_C11
S5_ALT_B1_B7_C10_C12
```

Never union the two S5 bases.

## 7. System invariants

Normalized bases:

```text
S1 = B1–B7
S2 = B1–B8
S3 = B1–B7 + A8
S4 = B1–B7 + C10
S5 primary = B1–B7 + C11
S5 alternative = B1–B7 + C10 + C12
```

Do not reintroduce A1–A7 as a second executable primitive list.

Do not claim A1–A6 are all literal copies of B1–B6.

A2, A4, and A7 require S1 theorem/bridge treatment.

## 8. Forbidden shortcuts

Do not introduce:

- unrestricted necessitation;
- Box into the M0 native language;
- B9 into the initial core;
- semantic validity as a proof step;
- tableau/sequent/natural-deduction rules as native proof steps;
- modern K/T/S4/S5 axioms as replacements for Lewis bases;
- object-language `=`;
- implicit definitional conversion;
- mixed-basis S5 proof checking.

## 9. Occurrence paths

`Sb` and `definition_conversion` use the single logical grammar defined in `spec/rules.yaml`:

```text
[]
[arg]
[left]
[right]
...
```

Dotted paths are renderer-only.

## 10. Search is untrusted

Future search may be sophisticated, but `PROVED` is emitted only after trusted certificate checking.

Search failure means:

```text
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
```

unless a separate decision procedure is certified.

## 11. Formula regression lock

The schema and definition ASTs source-checked by the first foundational audit are locked by:

```text
audit/m0/certified_ast_fingerprints.yaml
```

Changing a locked AST is a foundational change requiring source re-audit.

## 12. Testing discipline

Logic-sensitive changes require:

- structural validation;
- source-register validation;
- freeze-readiness validation where applicable;
- positive tests;
- mutation/rejection tests;
- exact-basis rejection tests;
- no tracked `*:Zone.Identifier`.

## 13. Change control

Any change to object language, definition semantics, primitive schema ASTs, primitive Lewis rules, certificate kinds/payloads, occurrence paths, or basis IDs/basis membership requires explicit foundational review.

Do not bundle such changes into ordinary refactors.
