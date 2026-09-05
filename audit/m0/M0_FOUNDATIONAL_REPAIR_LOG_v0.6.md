# M0 Foundational Repair Log v0.6

**Repair basis:** `M0_FOUNDATIONAL_P2_CLOSURE_RECHECK_2026-09-05.md`  
**Audited predecessor:** `5436a3d2a8a7eecefc26712c2505f1b271c4c200`

## 1. Exact failure in M0.5

M0.5 correctly established a single machine-readable certificate authority and
closed the nine duplicate-authority mutation holes. During that migration it
removed the old `certificate_serialization` registry without migrating one rule
that the previous audit had already accepted:

```text
duplicate_mapping_keys_policy: reject
```

The resulting sole contract therefore left the serialized-document decoder
boundary underdetermined. A permissive JSON/YAML parser could collapse duplicate
keys while a strict parser rejected them, and both could claim conformance.

No formula AST, definition AST, normalized basis, Lewis operation, or S5 bridge
is implicated.

## 2. M0.6 repair

The lost rule is restored **inside the existing sole authority**:

```text
spec/rules.yaml#canonical_certificate_contract.document_boundary
```

No second certificate-serialization registry is introduced.

M0.6 fixes one trusted serialized format:

```text
utf8_json_rfc8259_object
```

with these boundary requirements:

```text
strict UTF-8 decoding
UTF-8 BOM rejected
top-level JSON object
duplicate object-member names rejected recursively
rejection happens before mapping construction
exact Unicode-codepoint key identity after JSON string decoding
lone Unicode surrogate scalar strings rejected
NaN / Infinity / -Infinity rejected
decoded certificate values restricted to objects, arrays, and strings
logical checking begins only after successful strict decode
```

Other UI/import formats may exist only outside the trusted M0 certificate
boundary and must convert to the canonical JSON document first.

## 3. Why JSON is fixed at the trusted boundary

The preceding audit required either a fixed serialized certificate format or a
canonical decoding interface. M0.6 chooses one fixed interchange format rather
than leaving parser behavior implementation-defined.

This is a representation-layer decision only. Human proof rendering remains
independent of the machine certificate encoding.

## 4. Conformance fixture

M0.6 adds:

```text
scripts/certificate_document_conformance.py
```

It is validation infrastructure, not M1 kernel code.

Its JSON decoder uses pair-preserving object decoding so duplicate names are
detected before object construction. The fixture also rejects invalid UTF-8 and
nonstandard JSON constants.

## 5. Direct document-level tests

The new tests reject:

- duplicate top-level `root`;
- duplicate nested justification `kind`;
- duplicate nested formula `name`;
- duplicate names that become equal only after JSON escape decoding;
- nonstandard `NaN`;
- invalid UTF-8 input;
- a UTF-8 BOM;
- lone surrogate strings;
- numbers, booleans, and `null` in the strict certificate profile.

A valid canonical JSON certificate object decodes successfully.

The freeze suite additionally mutates the sole canonical field:

```text
duplicate_mapping_keys_policy
```

from `reject_before_mapping_construction` to an accepting behavior and requires
both the direct contract check and whole-contract fingerprint to fail.

## 6. Whole-contract lock

The certificate contract is bumped from version `1.0` to `1.1` and the lock to
`0.2`.

The lock records repair parent:

```text
5436a3d2a8a7eecefc26712c2505f1b271c4c200
```

and a new SHA-256 of the complete canonical contract including the document
boundary.

## 7. Audit accounting

`M0-C05` is reopened because M0.5 incorrectly left closed-world serialization
marked closed after losing the duplicate-key invariant.

New M0.6 pending items:

```text
M0-C06  canonical certificate document decoding boundary
M0-V04  duplicate-key validator/conformance coverage
M0-FP04 whole-contract lock after restoration
```

These may become `closed` only after the next exact-SHA closure recheck.

## 8. Non-regression

M0.6 intentionally does not alter:

- B1–B8;
- A8;
- C10–C12;
- DEF_OR;
- DEF_STRICT_IMP;
- DEF_EQUIV_S;
- normalized S1–S5 basis membership;
- S5 bridge orientation.

No historical formula/source re-audit is requested.

## 9. M1 gate

M1 remains forbidden until one narrow exact-SHA recheck returns:

```text
M0 FOUNDATIONAL SPECIFICATION CERTIFIED
```
