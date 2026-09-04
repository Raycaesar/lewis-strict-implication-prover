# M0 freeze checklist

Do not mark M0 frozen until every item below is checked.

## A. Repository and CI

- [ ] `python scripts/validate_spec.py` passes.
- [ ] `python scripts/validate_source_register.py` passes.
- [ ] `pytest` passes.
- [ ] GitHub Actions passes on the exact candidate freeze commit.
- [ ] no `*:Zone.Identifier` files are tracked.
- [ ] the candidate freeze commit SHA is recorded in the final audit report.

## B. Language and definitions

- [ ] primitive/core AST mapping is source-verified.
- [ ] 11.01 / `DEF_OR` is source-verified.
- [ ] 11.02 / `DEF_STRICT_IMP` is source-verified.
- [ ] 11.03 / `DEF_EQUIV_S` is source-verified.
- [ ] object-language `=` remains forbidden.
- [ ] `equiv_s` kernel status is deterministic and documented.
- [ ] definition conversion is deterministic and certificate-checkable.
- [ ] no Box constructor/sugar enters M0.

## C. Primitive operations

- [ ] Sa corresponds to L&L Substitution (b).
- [ ] Sb corresponds to L&L Substitution (a).
- [ ] Ad corresponds to L&L Adjunction.
- [ ] Smp corresponds to L&L Inference.
- [ ] all four are clearly identified as project labels.
- [ ] no unrestricted necessitation is enabled.
- [ ] B7 is not confused with the metalevel Inference operation.

## D. Schemas

- [ ] B1–B7 ASTs independently checked against L&L.
- [ ] B8 AST independently checked.
- [ ] A8 AST independently checked.
- [ ] C10 AST independently checked.
- [ ] C11 AST independently checked.
- [ ] C12 AST independently checked.
- [ ] A1–A7 nonduplication wording is accurate.
- [ ] B9 remains outside M0.

## E. Systems and normalization

- [ ] S1 = B1–B7.
- [ ] S2 = B1–B8.
- [ ] S3 normalized basis S1+A8 is explicitly distinguished from historical A1–A8.
- [ ] Parry support for the normalized S3 basis is verified.
- [ ] S4 = B1–B7+C10.
- [ ] S5 primary = B1–B7+C11.
- [ ] S5 alternative = B1–B7+C10+C12.
- [ ] theorem inclusion remains distinct from primitive-basis inheritance.

## F. Certificate architecture

- [ ] schema-instance semantics fixed.
- [ ] Sa payload fixed.
- [ ] Sb occurrence-path grammar fixed.
- [ ] Ad payload fixed.
- [ ] Smp payload fixed.
- [ ] definition-conversion payload fixed.
- [ ] derived theorem/macro calls are never kernel primitives.
- [ ] bridge calls require checked target-system expansions.

## G. Independent audit

- [ ] Work Max audit performed from scratch.
- [ ] no P0 foundational blocker remains.
- [ ] no P1 mathematical/specification defect remains.
- [ ] final verdict is `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`.

Only after all boxes are checked may the repository mark:

```text
M0 FROZEN
```

and begin M1.
