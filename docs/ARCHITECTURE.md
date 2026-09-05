# Architecture
## M0.6 duplicate-key boundary closure candidate

## 1. Trust layering

```text
historical sources
      ↓
formula/system specification
      ↓
single canonical certificate contract
      ↓
canonical certificate-document decoder boundary
      ↓
future trusted M1 kernel
      ↓
untrusted proof library/search
      ↓
renderer / UI
```

## 2. Single certificate authority

The only machine-readable certificate-semantics authority is:

```text
spec/rules.yaml#canonical_certificate_contract
```

`docs/PROOF_CERTIFICATE_SPEC.md` is a nonnormative human-readable rendering.

`lewis_operations` in `rules.yaml` is provenance/label metadata only and may
contain no executable rule semantics beyond its `contract_kind` link.

The validator rejects reintroduction of the former duplicate semantic
registries.

## 3. Canonical serialized-document boundary

Serialized input reaches the trusted logical certificate layer only after
passing:

```text
canonical_certificate_contract.document_boundary
```

M0.6 fixes one trusted interchange representation:

```text
strict UTF-8 JSON object
```

The decoder must reject duplicate member names recursively before an object is
collapsed into a mapping. Duplicate comparison is performed on decoded member
names by exact Unicode codepoint sequence; first-wins and last-wins behavior are
forbidden.

The conformance fixture:

```text
scripts/certificate_document_conformance.py
```

tests this boundary. It is validation infrastructure, not the M1 theorem
checker.

Other frontend formats are outside the trusted boundary and must convert to the
canonical JSON representation first.

## 4. Future M1 responsibilities

The trusted kernel will implement the canonical contract and canonical document
boundary, including:

- strict document decoding;
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

## 5. Contract change control

The complete canonical contract, including `document_boundary`, has a freeze
fingerprint.

Any ordinary semantic edit causes `--freeze` failure. A deliberate simultaneous
contract+fingerprint edit cannot be authenticated by the local validator and is
therefore a foundational change requiring focused independent re-audit.
