# Lewis S1–S5 Native Syntactic Prover
## Foundational specification v0.6

**Status:** narrow certificate-document-boundary closure candidate  
**Logical layer:** unchanged from the already-audited M0.4/M0.5 candidates.

## 1. M0.5 audit result and M0.6 scope

M0.5 successfully established one machine-readable certificate authority and
closed the prior duplicate-authority freeze defect.

Its narrow closure recheck nevertheless found one migration regression:

```text
duplicate serialized mapping/object keys were no longer normatively required
to be rejected before logical checking
```

That omission allowed two otherwise conforming implementations to differ at the
document-decoding boundary.

M0.6 repairs only that lost serialization invariant. It does not reopen or
change the Lewis calculus.

## 2. Logical non-regression

Unchanged:

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

There is exactly one machine-readable certificate-semantics authority:

```text
spec/rules.yaml#canonical_certificate_contract
```

It contains the closed logical object grammar, identifiers, occurrence paths,
all six trusted certificate kinds, DAG requirements, metadata policy, and the
serialized-document boundary.

Former executable mirrors remain forbidden:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

No second serialization registry is introduced by M0.6.

## 4. Canonical certificate-document boundary

The normative subtree is:

```text
canonical_certificate_contract.document_boundary
```

M0.6 admits exactly one trusted serialized representation:

```text
strict UTF-8 JSON object
```

Before logical validation:

- bytes are decoded as strict UTF-8;
- the top-level decoded value must be a JSON object;
- duplicate JSON object member names are rejected recursively;
- duplicate detection happens before map construction/collapse;
- duplicate-name identity is exact Unicode codepoint sequence after JSON string
  decoding;
- first-wins and last-wins duplicate behavior are forbidden;
- nonstandard `NaN`, `Infinity`, and `-Infinity` constants are rejected;
- the project strict profile rejects BOMs, lone surrogate scalar strings, and
  non-string/non-container decoded certificate values.

Other human or UI import formats may exist only outside the trusted M0 boundary.
They must be converted into this canonical JSON form before trusted
certificate-document acceptance.

## 5. Decoder conformance fixture

The repository includes:

```text
scripts/certificate_document_conformance.py
```

This is M0 validation infrastructure, not M1 theorem-checker implementation.

It exercises the normative document boundary, including recursive duplicate-key
detection before object construction.

## 6. Human documentation status

Human-readable certificate documentation is explicitly a:

```text
nonnormative rendering of the canonical contract
```

If prose and canonical YAML disagree, M1 must follow the canonical YAML and
report the documentation defect.

## 7. Whole-contract freeze lock

The complete canonical contract, including the restored document boundary, is
canonicalized and SHA-256 locked in:

```text
audit/m0/certificate_contract_lock.yaml
```

`validate_spec.py --freeze` recomputes the hash.

A deliberate simultaneous contract+hash edit is not authenticated by the local
validator and therefore remains a foundational change requiring focused
independent re-audit.

## 8. S5 bridge non-regression

Already repaired bridge semantics remain unchanged:

```text
from_basis_id
into_basis_id
expanded_certificate.basis_id == into_basis_id
```

Directions remain:

```text
primary -> alternative : recover C11 under alternative
alternative -> primary : recover C10,C12 under primary
```

## 9. Freeze gate

The exact candidate must pass:

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
python -m pytest
```

The suite must directly reject duplicate top-level and nested certificate
members and must reject a mutation that changes the canonical duplicate-key
policy to an accepting behavior.

## 10. M1 gate

M1 remains forbidden until an exact-SHA narrow closure recheck returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
