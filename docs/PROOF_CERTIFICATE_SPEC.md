# Proof Certificate Specification
## M0.5 human-readable rendering

**Normative status:** NONNORMATIVE RENDERING.

The sole machine-readable authority for certificate acceptance is:

```text
spec/rules.yaml#canonical_certificate_contract
```

This document explains that object. It does not create a second normative
certificate grammar. If this document and the canonical YAML differ, the YAML
controls M1 implementation and the prose discrepancy must be reported and
repaired.

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
