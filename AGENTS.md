# AGENTS.md

## Current milestone

M0.5 is a narrow freeze-integrity closure candidate. Do not implement M1 until
an exact-SHA independent recheck certifies M0.

## Machine-readable authorities

Formula/system authorities:

```text
spec/language.yaml
spec/schemas.yaml
spec/systems.yaml
```

Certificate authority:

```text
spec/rules.yaml#canonical_certificate_contract
```

This is the **sole machine-readable certificate-semantics authority**.

Do not implement semantics from any removed legacy registry or from explanatory
prose.

## Human documentation

`docs/PROOF_CERTIFICATE_SPEC.md` and certificate sections of other Markdown
files are nonnormative renderings. If they conflict with the canonical YAML,
follow the YAML for implementation and report the documentation defect.

## Forbidden duplicate semantic registries

Do not reintroduce active top-level keys:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

`lewis_operations` is provenance metadata only and must contain no executable
semantics beyond a `contract_kind` link.

## Logical invariants

Do not change the audited B1–B8, A8, C10–C12 or 11.01–11.03 ASTs without a new
foundational source audit.

Do not add Box, B9, unrestricted necessitation, object-language `=`, semantic
proof steps, mixed-basis S5 checking, or implicit definition conversion.

## Contract change control

The entire canonical certificate contract is fingerprinted. A deliberate
contract+fingerprint change is a foundational change requiring focused
independent re-audit.
