# Lewis S1–S5 Native Syntactic Prover
## Foundational specification v0.5

**Status:** narrow P2 closure candidate  
**Logical layer:** unchanged from the independently audited M0.4 candidate.

## 1. What changed in M0.5

The second closure recheck found no P0 and no P1. It found one freeze-integrity
P2: `spec/rules.yaml` duplicated certificate semantics across old fields and new
policy mirrors, while the freeze validator protected only some copies.

M0.5 removes that duplication.

There is now exactly one machine-readable certificate-semantics authority:

```text
spec/rules.yaml#canonical_certificate_contract
```

No other active field in `rules.yaml` is allowed to restate executable
certificate semantics.

## 2. Logical non-regression

The following are unchanged:

```text
B1–B8
A8
C10–C12
DEF_OR
DEF_STRICT_IMP
DEF_EQUIV_S
```

Normalized bases remain:

```text
S1 = B1–B7
S2 = B1–B8
S3 = B1–B7 + A8
S4 = B1–B7 + C10
S5 primary = B1–B7 + C11
S5 alternative = B1–B7 + C10 + C12
```

No Box, B9, unrestricted necessitation, semantic proof rule, or mixed S5 basis
is introduced.

## 3. Sole certificate authority

`canonical_certificate_contract` contains, in one tree:

- closed-world top-level certificate fields;
- exact node fields;
- identifier/reference types and exact string identity;
- occurrence-path semantics;
- every trusted justification kind;
- postulate-instance semantics;
- `Sa`, `Sb`, `Ad`, `Smp`;
- `definition_conversion`;
- proof-DAG invariants;
- trusted metadata policy.

The former active mirrors are removed:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

If any of these legacy semantic keys is reintroduced, validation fails.

## 4. Lewis-operation provenance

`lewis_operations` contains only:

```text
project_label
name
contract_kind
source
```

for `Sa`, `Sb`, `Ad`, `Smp`.

It carries historical provenance and links to the canonical contract kind. It
does not duplicate operational semantics.

## 5. Human documentation status

Human-readable certificate documents are explicitly:

```text
nonnormative renderings of the canonical contract
```

They may explain the canonical YAML but cannot override it. A discrepancy is a
documentation defect; an M1 implementation must follow the canonical contract
and report the discrepancy rather than choose between competing declarations.

## 6. Whole-contract freeze lock

The complete canonical contract is canonicalized and SHA-256 locked in:

```text
audit/m0/certificate_contract_lock.yaml
```

`validate_spec.py --freeze` recomputes the hash.

Therefore any ordinary semantic mutation anywhere inside the sole canonical
contract fails the freeze gate, including mutations that previously slipped
through duplicate old fields.

A deliberate simultaneous edit of the contract and its stored hash cannot be
authenticated automatically. The lock explicitly classifies that operation as
a foundational certificate-contract change requiring focused independent
re-audit.

## 7. Bridge semantics

M0.4's already repaired operational bridge semantics remain unchanged:

```text
from_basis_id
into_basis_id
expanded_certificate.basis_id == into_basis_id
```

S5 directions remain:

```text
primary -> alternative : recover C11 under alternative
alternative -> primary : recover C10,C12 under primary
```

## 8. Freeze gate

The exact candidate must pass:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

The test suite must also replay:

- the five original semantic mutations accepted by M0.4;
- the four serialization mutations accepted by M0.4;
- injection of each forbidden legacy semantic top-level field;
- whole-contract fingerprint mutation;
- existing bridge/provenance/status checks.

## 9. M1 gate

M1 remains forbidden until an exact-SHA narrow closure recheck returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
