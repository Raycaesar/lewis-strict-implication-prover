# Safe M0 specification repair notes

This package makes only **source/provenance and wording repairs** that are
already clear from the primary/secondary sources. It does not silently resolve
the open `equiv_s`/definition-conversion design question.

## Repairs included

### `spec/rules.yaml`

- `historical_label` is replaced by `project_label`.
- exact L&L printed-page/heading/clause provenance is added.
- Feys cross-check labels are added.
- no primitive rule is added or removed.

### `spec/schemas.yaml`

- printed page provenance is strengthened.
- the A-series explanation is corrected:
  - no longer says A1–A6 are all formula-for-formula duplicates;
  - states that separate A1–A7 executable copies are unnecessary in the
    normalized presentation;
  - cites Parry's S3 reconstruction as support.
- no schema AST is changed in this package.

### `spec/systems.yaml`

- the S3 normalized basis note is strengthened with Parry 1939 pp. 137–138.
- wording distinguishes literal historical basis from normalized prover basis.
- no system's executable schema set is changed.

### validation infrastructure

- rule-label tests now check `project_label`.
- source-register validation is added.
- CI runs both structural validation and source-register validation.

## Not repaired automatically

These remain explicit Work Max / M0 closure questions:

1. kernel-level status of `equiv_s`;
2. deterministic definition expansion/contraction policy;
3. exact certificate representation of visible definition conversion.
