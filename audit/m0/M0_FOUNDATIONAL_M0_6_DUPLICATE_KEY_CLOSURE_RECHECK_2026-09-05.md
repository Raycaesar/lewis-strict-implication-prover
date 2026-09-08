M0 FOUNDATIONAL SPECIFICATION CERTIFIED

# Work Max — narrow closure recheck of the M0.6 duplicate-key boundary repair

Audit date: 2026-09-05  
Repository: `Raycaesar/lewis-strict-implication-prover`  
Supplied revision: `21117f3`  
Audited commit: `21117f3da827f873c3ed88b578a1681aabfca7ac`  
Audited tree: `25b2e20af085625285c6f8bd6ab5a1b1c5b66a09`  
Parent: `5436a3d2a8a7eecefc26712c2505f1b271c4c200`

## 1. Overall verdict

**Certified.** Commit `21117f3da827f873c3ed88b578a1681aabfca7ac` fully restores the certificate-document duplicate-key invariant lost in M0.5. The repair is inside the existing sole machine-readable authority, fixes one exact trusted serialized format, rejects duplicate JSON member names recursively before any first-wins/last-wins collapse, and is protected by both direct freeze assertions and the whole-contract lock.

The prior certificate-document P1 and its dependent freeze/accounting P2 are substantively closed. No P0, P1, or freeze-undermining P2 remains. Direct comparison with the failed predecessor confirms that the 12 schema ASTs, three definition ASTs, normalized S1–S5 bases, S5 bridge records, and certified AST fingerprint file did not change.

Two independent M1 implementations following the canonical contract are now forced to accept the same logical class of serialized certificate documents: strict UTF-8 JSON objects satisfying the project’s closed strict profile. No parser choice may silently collapse duplicates or admit an alternate trusted serialization.

**M0 may be frozen. M1 trusted-kernel implementation may begin after the administrative frozen-status commit described in section 12.**

## 2. Scope and immutable candidate identity

The supplied short revision resolves uniquely to [commit `21117f3da827f873c3ed88b578a1681aabfca7ac`](https://github.com/Raycaesar/lewis-strict-implication-prover/commit/21117f3da827f873c3ed88b578a1681aabfca7ac), titled `M0 repair-5`. The audit used a clean detached worktree at that exact object. Its parent is exactly the previously audited failed candidate `5436a3d2a8a7eecefc26712c2505f1b271c4c200`; no later state of `main` was used.

The requested files were read in the stated order. The historical formula/source audit was not repeated because direct parsed-object comparison and the unchanged certified fingerprint file established non-regression of every protected formula, definition, system basis, and S5 bridge object.

## 3. Closure checklist

| Mandatory area | Result | Conclusion |
| --- | --- | --- |
| A. Sole-authority preservation | **Pass** | `canonical_certificate_contract.document_boundary` is within the sole authority; no legacy serialization registry or executable mirror was reintroduced. |
| B. Exact serialized boundary | **Pass** | One strict UTF-8 JSON-object format is fixed, including duplicate, BOM, Unicode-string, constant, and decoded-value policies. |
| C. Duplicate-key probes | **Pass** | All four required duplicate documents reject with `DuplicateCertificateKeyError`; a permissive policy mutation fails freeze. |
| D. Whole-contract lock | **Pass** | Independent SHA-256 recomputation matches, covers `document_boundary`, and changes when the duplicate policy changes. |
| E. Audit accounting | **Pass** | `M0-C05` is reopened and all four current repair items remain `repair_implemented_reaudit_pending` until certification is administratively recorded. |
| F. Commands and exact-SHA CI | **Pass** | All local gates pass; 44 tests pass; hygiene is clean; exact-SHA Actions succeeds. |
| G. Non-regression | **Pass** | Protected ASTs, bases, bridge records, and AST fingerprints are unchanged from `5436a3d2…`. |

## 4. A — sole-authority preservation

The normative repair appears at [`spec/rules.yaml:218–236`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/spec/rules.yaml#L218-L236), inside:

```text
spec/rules.yaml#canonical_certificate_contract.document_boundary
```

The parsed top level of `spec/rules.yaml` contains exactly:

```text
canonical_certificate_contract
component
explicitly_forbidden_rules
lewis_operations
non_rules
project
scope
spec_version
status
```

None of the seven former executable registries is present:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

The validator closes the rules-file top level and expressly rejects all seven names at [`scripts/validate_spec.py:65–74`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/scripts/validate_spec.py#L65-L74) and [`:338–357`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/scripts/validate_spec.py#L338-L357). An independent injection of `certificate_serialization` produced both `RULES_TOPLEVEL_KEYS` and `LEGACY_RULES_SEMANTICS`.

Each `lewis_operations` entry has only `project_label`, `name`, `contract_kind`, and `source`. An independent semantic-field injection under `lewis_operations.Sa` produced `LEWIS_OPERATION_FIELDS`. These entries therefore remain provenance/link metadata and cannot extend executable certificate semantics.

The three-field `canonical_document_boundary` entry in `audit/m0/source_register.yaml` is an audit-coherence record, not an implementation authority: the same enclosing record identifies the one authoritative path, forbids duplicate machine-readable semantics, and labels human documentation nonnormative. It is not consulted by certificate acceptance, and its validator only detects provenance drift. It therefore does not constitute a second active certificate grammar.

The implementation hierarchy is explicit in [`AGENTS.md:18–50`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/AGENTS.md#L18-L50). [`docs/PROOF_CERTIFICATE_SPEC.md:4–15`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/docs/PROOF_CERTIFICATE_SPEC.md#L4-L15) is explicitly a nonnormative rendering and cannot override the YAML.

## 5. B — exact serialized certificate boundary

The canonical document profile is precise and closed:

| Boundary question | Normative answer | Verification |
| --- | --- | --- |
| Trusted format | Exactly `utf8_json_rfc8259_object` | The accepted-format list has one member. |
| Byte decoding | Strict UTF-8 | Invalid UTF-8 rejects before JSON parsing. |
| Top-level value | JSON object | Arrays and strings reject with `CertificateTopLevelTypeError`. |
| Duplicate names | Reject recursively in every JSON object | Root, justification, and formula duplicates all reject. |
| Rejection timing | Before mapping collapse/logical validation | Pair-preserving decoding raises on the repeated decoded name; no first/last-wins logical map is returned. |
| Name identity | Exact Unicode code-point sequence after JSON string decoding | `root` and `r\u006fot` collide; canonically distinct sequences such as `é` and `e` + combining acute remain distinct. |
| Nonstandard constants | Reject `NaN`, `Infinity`, `-Infinity` | All three reject through `parse_constant`. |
| BOM | Reject | Both byte-level UTF-8 BOM and a leading decoded U+FEFF reject. |
| Decoded strings | Unicode scalar values only; no surrogate code points | Lone surrogate values and member names reject; a valid paired non-BMP escape decodes to one scalar and is accepted. |
| Decoded value types | Objects, arrays, and strings only | Integers, floats, booleans, and `null` reject before logical validation. |
| Validation order | Strict document decode first | The logical checker receives a mapping only after the complete profile succeeds. |
| Other frontend formats | Outside the trusted M0 boundary | They must first convert to the canonical JSON document and cannot enlarge kernel acceptance. |

The normative fields are at [`spec/rules.yaml:218–236`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/spec/rules.yaml#L218-L236). The supplied conformance fixture implements the same boundary at [`scripts/certificate_document_conformance.py:46–145`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/scripts/certificate_document_conformance.py#L46-L145). The fixture is validation infrastructure, not M1 kernel code; the YAML remains the authority.

### Independent-implementation question

**Are two independent M1 implementations forced to agree on accepted serialized logical certificate documents? Yes.**

Agreement no longer depends on a host parser’s default duplicate-key behavior. The contract selects one encoding and syntax, specifies when decoded names are compared, excludes ambiguous or nonstandard scalar forms from the project profile, and makes successful strict decoding a precondition of logical validation. Alternate import formats terminate outside the trusted boundary and cannot directly enter kernel validation.

## 6. C — duplicate-key conformance probes

The repository tests directly exercise the serialized document decoder rather than a pre-collapsed mapping. The four mandatory cases produced:

| Document mutation | Result |
| --- | --- |
| Duplicate top-level `root` | Rejected: `DuplicateCertificateKeyError` |
| Duplicate nested justification `kind` | Rejected: `DuplicateCertificateKeyError` |
| Duplicate nested formula field | Rejected: `DuplicateCertificateKeyError` |
| Names equal only after JSON escape decoding | Rejected: `DuplicateCertificateKeyError` |

The direct fixtures are at [`tests/spec/test_certificate_document_boundary.py:51–93,130–138`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/tests/spec/test_certificate_document_boundary.py#L51-L138). The dedicated file passes all 12 tests.

An independent probe additionally confirmed rejection of invalid UTF-8, BOMs, top-level non-objects, all three named nonstandard constants, numeric/boolean/null values, lone surrogate values and member names, and YAML text presented at the trusted JSON boundary. A valid minimal document and a valid non-BMP Unicode scalar were accepted.

Mutating only the authoritative field:

```text
canonical_certificate_contract.document_boundary.duplicate_mapping_keys_policy
```

from `reject_before_mapping_construction` to `last_wins` caused `validate_bundle(..., freeze=True)` to return:

```text
CONTRACT_DOCUMENT_BOUNDARY
FINGERPRINT_CONTRACT
```

This is an authority-level mutation test, not a mirror-only assertion.

## 7. D — whole-contract lock

[`audit/m0/certificate_contract_lock.yaml`](https://github.com/Raycaesar/lewis-strict-implication-prover/blob/21117f3da827f873c3ed88b578a1681aabfca7ac/audit/m0/certificate_contract_lock.yaml) records:

```text
lock_version: 0.2
repair_parent_commit: 5436a3d2a8a7eecefc26712c2505f1b271c4c200
contract_path: spec/rules.yaml#canonical_certificate_contract
contract_version: 1.1
canonical_contract_sha256: c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316
```

Using independently produced canonical JSON (`sort_keys`, compact separators, UTF-8 without ASCII escaping), the complete current `canonical_certificate_contract` hashes to exactly:

```text
c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316
```

The hashed tree includes `document_boundary`. Changing its duplicate-key policy changes the digest and produces `FINGERPRINT_CONTRACT`; changing the field to an accepting value also independently produces `CONTRACT_DOCUMENT_BOUNDARY`.

The documented limitation is accurate: the local hash is a change detector, not an external authentication mechanism. A deliberate simultaneous contract-and-hash edit can pass local digest comparison but is expressly a foundational change requiring focused independent re-audit. That limitation does not undermine this exact-SHA freeze.

## 8. E — audit accounting and administrative transition

The accounting is truthful at the candidate commit:

| Obligation | Candidate status | Assessment |
| --- | --- | --- |
| `M0-C05` — closed-world certificate serialization | `repair_implemented_reaudit_pending` | Correctly reopened after the M0.5 regression. |
| `M0-C06` — canonical document-decoding boundary | `repair_implemented_reaudit_pending` | Repair implemented; this recheck supplies closure evidence. |
| `M0-V04` — duplicate-key validation/conformance | `repair_implemented_reaudit_pending` | Repair implemented; direct and mutation tests pass. |
| `M0-FP04` — updated whole-contract lock | `repair_implemented_reaudit_pending` | Repair implemented; independent digest verification passes. |

The source register likewise remains `candidate_source_audit`, and its certificate-contract entry remains re-audit pending. This is correct before the present verdict; the repository did not falsely pre-close its own external audit.

The freeze validator encodes both sides of the transition: candidate mode requires the four items to remain pending, while frozen mode requires them to be closed and forbids any remaining re-audit-pending item. The two supplied post-certification transition tests pass, demonstrating that the administrative candidate-to-frozen update is not blocked.

## 9. F — validators, tests, hygiene, and exact-SHA CI

### Local gates

| Command | Result |
| --- | --- |
| `python scripts/validate_spec.py` | PASS — M0.6; 7 constructors, 12 schemas, 4 Lewis operations, 6 certificate kinds, 5 systems |
| `python scripts/validate_source_register.py` | PASS |
| `python scripts/validate_spec.py --freeze` | PASS |
| `python scripts/validate_source_register.py --freeze` | PASS |
| `python -m pytest` | PASS — `44 passed in 1.05s` |
| `git ls-files '*:Zone.Identifier'` | PASS — no output |

The candidate worktree remained clean after validation.

### Exact-SHA GitHub Actions

[GitHub Actions run 33947209250](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/33947209250) is a completed successful push run with `head_sha` exactly `21117f3da827f873c3ed88b578a1681aabfca7ac`. Its `validate-m0-spec` job succeeded at every relevant step:

- tracked `Zone.Identifier` rejection;
- executable specification validation;
- source-register validation;
- M0.6 spec freeze readiness;
- M0.6 source/audit freeze readiness;
- the complete pytest suite.

The workflow covers `spec/**`, `audit/m0/**`, `scripts/**`, `tests/spec/**`, the workflow itself, and the relevant documentation/configuration paths. This exact candidate therefore has both local and remote exact-SHA gate evidence.

These gates establish structural conformance, mutation rejection, lock integrity, and regression protection. They are not a substitute for the earlier mathematical/source audit; certification relies on that accepted layer remaining byte/AST-equivalent, as independently checked below.

## 10. G — formula, definition, basis, and bridge non-regression

Direct comparison against parent `5436a3d2a8a7eecefc26712c2505f1b271c4c200` produced:

| Protected object | Result |
| --- | --- |
| 12 schema ASTs: B1–B8, A8, C10–C12 | Exact equality for every parsed AST |
| Three definition ASTs: DEF_OR, DEF_STRICT_IMP, DEF_EQUIV_S | Exact equality of every `lhs` and `rhs` |
| S1 normalized basis | Unchanged: B1–B7 |
| S2 normalized basis | Unchanged: B1–B8 |
| S3 normalized basis | Unchanged: B1–B7 + A8 |
| S4 normalized basis | Unchanged: B1–B7 + C10 |
| S5 primary basis | Unchanged: B1–B7 + C11 |
| S5 alternative basis | Unchanged: B1–B7 + C10 + C12 |
| Both S5 bridge-obligation objects | Exact parsed-object equality |
| `certified_ast_fingerprints.yaml` | Byte-for-byte unchanged |

The only changes in `spec/language.yaml`, `spec/schemas.yaml`, and `spec/systems.yaml` are their version strings from `0.5` to `0.6`.

The already-correct bridge orientation remains:

| Bridge use | `from_basis_id` | `into_basis_id` | Expanded certificate derives under |
| --- | --- | --- | --- |
| Primary → alternative: recover C11 | `S5_PRIMARY_B1_B7_C11` | `S5_ALT_B1_B7_C10_C12` | Alternative basis |
| Alternative → primary: recover C10, C12 | `S5_ALT_B1_B7_C10_C12` | `S5_PRIMARY_B1_B7_C11` | Primary basis |

No formula/source layer was silently changed, so reopening the completed B1–C12, 11.01–11.03, Parry, or S5 source audit is neither necessary nor justified.

## 11. Defect register

| Severity | Open defects | Disposition |
| --- | ---: | --- |
| P0 | 0 | None. |
| P1 | 0 | The duplicate-key certificate-document boundary is deterministic and closed. |
| P2 affecting freeze integrity | 0 | Validator, lock, accounting, transition, CI, and direct conformance coverage are adequate. |
| P3 | 0 | No optional hardening item is necessary to qualify this certification. |

No new defect was found in the narrow repair, and no previously closed formula/source defect was reopened.

## 12. Final recommendation and freeze handoff

Commit `21117f3da827f873c3ed88b578a1681aabfca7ac` is a safe immutable logical basis for M1. The lost duplicate-key invariant is restored in the sole authority, the serialized-document acceptance set is deterministic across independent implementations, direct duplicate documents reject before any lossy collapse, and the authoritative field is protected by both exact validation and a whole-contract fingerprint.

The next commit should be administrative only:

1. record this exact-SHA certification report;
2. change the four `spec/*.yaml` statuses from `candidate_m0` to `frozen_m0`;
3. change the source-register status to `frozen_source_audit` and its certificate-contract status to `closed`;
4. change `M0-C05`, `M0-C06`, `M0-V04`, and `M0-FP04` from `repair_implemented_reaudit_pending` to `closed`, citing this report;
5. make no change to formula ASTs, definition ASTs, bases, bridges, the canonical certificate contract, or either fingerprint digest; and
6. rerun the same local and exact-SHA CI gates.

**M0 may be frozen, and M1 trusted-kernel implementation may begin after that administrative frozen-status commit.**
