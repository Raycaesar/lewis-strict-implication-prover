# Architecture
## M0.5 closure candidate

## Trust layering

```text
historical sources
      ↓
formula/system specification
      ↓
single canonical certificate contract
      ↓
future trusted M1 kernel
      ↓
untrusted proof library/search
      ↓
renderer / UI
```

## Single certificate authority

The only machine-readable certificate-semantics authority is:

```text
spec/rules.yaml#canonical_certificate_contract
```

`docs/PROOF_CERTIFICATE_SPEC.md` is a nonnormative human-readable rendering.

`lewis_operations` in `rules.yaml` is provenance/label metadata only and may
contain no executable rule semantics.

The validator rejects reintroduction of the former duplicate semantic
registries.

## Future M1 responsibilities

The trusted kernel will implement exactly the canonical contract:

- formula validation;
- basis admission;
- schema instantiation;
- object substitution;
- occurrence paths;
- definition conversion;
- substitution of strict equivalents;
- adjunction;
- strict detachment;
- DAG integrity.

Search remains outside the trusted boundary.

## Contract change control

The complete canonical contract has a freeze fingerprint. Any ordinary edit
causes `--freeze` failure. Deliberate contract+fingerprint edits require focused
foundational re-audit and cannot be merged as ordinary refactoring.
