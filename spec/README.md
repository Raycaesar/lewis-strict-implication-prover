# Executable M0.6 specification

The certificate-semantics authority is exactly:

```text
rules.yaml#canonical_certificate_contract
```

There is no second executable certificate registry.

`lewis_operations` is historical provenance/label metadata only.

The validator rejects legacy duplicate certificate-semantics keys and, in
`--freeze` mode, fingerprints the complete canonical contract.
