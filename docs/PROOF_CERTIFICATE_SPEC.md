# Proof Certificate Specification
## M0.6 human-readable rendering

**Normative status:** NONNORMATIVE RENDERING.

The sole machine-readable authority for certificate acceptance is:

```text
spec/rules.yaml#canonical_certificate_contract
```

This document explains that object. It does not create a second normative
certificate grammar. If this document and the canonical YAML differ, the YAML
controls M1 implementation and the prose discrepancy must be reported and
repaired.


## Serialized document boundary

The canonical contract admits exactly one trusted serialized certificate format in M0.6:

```text
UTF-8 JSON object
```

The strict decoder rejects duplicate object-member names recursively **before** any JSON object is collapsed into a mapping. Thus duplicate `root`, `goal`, `nodes`, `conclusion`, `kind`, `direction`, or any other member name is a document error rather than a last-wins/first-wins choice.

Strict decoding also rejects invalid UTF-8, a UTF-8 BOM, lone Unicode surrogate scalar strings, and nonstandard JSON constants (`NaN`, `Infinity`, `-Infinity`). The M0.6 strict certificate profile contains only JSON objects, arrays, and strings; numbers, booleans, and `null` are rejected before logical validation.

Logical certificate checking starts only after successful strict decoding.

Other import formats, if later offered by the UI, are outside the trusted boundary and must convert to the canonical JSON document first.

## Certificate object

The canonical contract currently fixes a closed-world proof object with:

```text
proof_id
system
basis_id
goal
root
nodes
```

Each node contains only:

```text
conclusion
justification
```

Trusted kinds are:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

Only `Sa`, `Sb`, `Ad`, `Smp` are Lewis inference operations.
`definition_conversion` is checked metalinguistic use of a registered
definition.

## Core invariants rendered from the canonical contract

- identifiers and references are nonempty strings;
- reference lookup uses exact Unicode codepoint-string identity without scalar
  coercion;
- unknown logical fields are rejected;
- occurrence paths are lists over `arg`, `left`, `right`;
- `atom` has no traversable formula child;
- no definition expansion occurs during path traversal;
- postulate instantiation uses exactly the registered schema metavariable set;
- `Sa` is simultaneous, one-pass and nonrecursive into replacement values;
- `Sb` replaces exactly one selected occurrence and requires surface `equiv_s`;
- `definition_conversion` uses one shared metavariable environment and exactly
  one replacement;
- all Lewis rule matching is exact on surface ASTs;
- the proof graph is acyclic, reference-complete and root-reachable;
- trusted certificates contain no metadata field.

For exact field names and values, consult the canonical YAML rather than this
rendering.

## Basis discipline

Every proof declares one allowed basis ID. The two S5 bases are never unioned.

Bridge objects are outside the primitive certificate kinds. Their expansion
must check in `into_basis_id`.

## Change control

Changing the canonical contract is a foundational M0 change. The whole contract
is fingerprinted by `audit/m0/certificate_contract_lock.yaml`; changing both
contract and lock deliberately still requires focused independent re-audit.
