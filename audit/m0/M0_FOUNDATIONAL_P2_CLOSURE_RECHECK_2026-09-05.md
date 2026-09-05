M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED

# Work Max — narrow P2 closure recheck of the M0.5 single-authority certificate repair

Audit date: 2026-09-05  
Repository: `Raycaesar/lewis-strict-implication-prover`  
Supplied revision: `5436a3d`  
Audited commit: `5436a3d2a8a7eecefc26712c2505f1b271c4c200`  
Audited tree: `b6b422a0050d52501ebae1e04ba3144d7061b9e5`  
Parent: `5f86547a2f16e5f1e1620823e3b68457fb8350b7`

## 1. Overall verdict

**Not certified.** M0.5 successfully closes the previously reported duplicate-authority/freeze-gate defect in its narrow mechanical sense: there is one active machine-readable certificate contract, all seven legacy registries are absent and forbidden, the nine formerly accepted mutations now fail, the complete current contract is hash-locked, the local gates pass, and exact-SHA GitHub Actions is green.

The deduplication nevertheless introduced one new **P1 certificate-boundary regression**. M0.4 explicitly required duplicate mapping keys in serialized proof certificates to be rejected before logical checking. M0.5 deleted `certificate_serialization`, but did not transfer `duplicate_mapping_keys_policy: reject` into `spec/rules.yaml#canonical_certificate_contract`. The current contract is now the sole authority, and `AGENTS.md` directs M1 implementers not to recover semantics from old registries or explanatory prose. Consequently, the exact candidate no longer determines whether a proof document with duplicate mapping keys is rejected or collapsed by its parser.

This is not theoretical parser trivia. In an independent probe, PyYAML's ordinary safe loader parsed:

```yaml
root: first
root: second
```

as `{"root": "second"}`, while the repository's strict loader rejected the same text with `DuplicateKeyError`. Both behaviors remain compatible with the sole current contract because that contract says nothing about duplicate serialized keys. Two independent M1 implementations are therefore **not** forced to accept the same certificate documents.

No schema AST, definition AST, normalized basis membership, or S5 bridge direction changed. The required repair is confined to the certificate serialization boundary, its validator/test coverage, and closure documentation. M0 must not be frozen and M1 trusted-kernel implementation must not begin at this commit.

## 2. Scope and immutable candidate identity

The supplied short revision uniquely resolved to full commit `5436a3d2a8a7eecefc26712c2505f1b271c4c200`, titled `make M0 certificate contract single-authority`. The audit used a detached worktree at that exact object. The worktree was clean before and after inspection; no later `main` state was used and no repository file was edited.

The requested files were read in the stated order. Historical formula sources were not re-audited because direct parsed-object comparison established that all locked formula/definition ASTs and normalized bases are unchanged from the already-audited predecessor.

## 3. Closure checklist summary

| Mandatory area | Result | Finding |
| --- | --- | --- |
| A. One authoritative representation | **Partial / fail overall** | One machine authority now exists and duplicate registries are gone, but one previously normative serialization rule was lost rather than migrated. |
| B. Nine formerly accepted mutations | **Pass** | All nine mutations of the actual canonical tree produce one or more freeze issues. |
| C. Whole-contract lock | **Pass** | Independent SHA-256 recomputation matches; arbitrary changes within the canonical tree fail freeze. |
| D. Internal contradiction probes | **Pass for the requested probes** | Every legacy-key injection, a semantic field on a Lewis-operation entry, and a canonical semantic extension are rejected. |
| E. Commands and CI | **Pass** | Four validators pass, 32 tests pass, no tracked `Zone.Identifier` exists, and exact-SHA Actions succeeds. |
| F. Formula/system non-regression | **Pass** | Twelve schema ASTs, three definition ASTs, all normalized bases, and both S5 bridge records are unchanged. |
| Preservation of accepted certificate serialization semantics | **Fail** | Duplicate certificate mapping-key rejection disappeared from the sole authority. |

## 4. A — one authoritative representation

### 4.1 Structural single authority: pass

`spec/rules.yaml:9–217` declares `canonical_certificate_contract` with authority value `sole_machine_readable_certificate_authority`. The parsed top-level keys of `rules.yaml` are exactly:

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

None of the former active registries remains:

```text
primitive_rules
kernel_certificate_kinds
occurrence_path_grammar
proof_node_grammar
dag_invariants
certificate_serialization
trusted_kernel_invariant
```

`scripts/validate_spec.py:65–74,318–338` closes the `rules.yaml` top level and rejects every named legacy key. Independent injection of each of the seven names produced both `RULES_TOPLEVEL_KEYS` and `LEGACY_RULES_SEMANTICS`.

`lewis_operations` contains four entries, `Sa`, `Sb`, `Ad`, and `Smp`. Each actual entry contains only `project_label`, `name`, `contract_kind`, and `source`; the source data is historical provenance. `scripts/validate_spec.py:510–521` rejects any extra direct field. An independent `constraints: [extra executable semantics]` insertion under `lewis_operations.Sa` produced `LEWIS_OPERATION_FIELDS`.

The authority hierarchy is also unambiguous in human documentation:

- `AGENTS.md:18–33` identifies the canonical YAML as sole authority and makes Markdown nonnormative;
- `docs/FOUNDATIONAL_SPEC_v0.5.md:15–22,96–106` says prose cannot override that YAML;
- `docs/PROOF_CERTIFICATE_SPEC.md:4–15` labels itself `NONNORMATIVE RENDERING`;
- `audit/m0/source_register.yaml:447–452` registers one authority and forbids duplicate machine semantics.

### 4.2 Semantic migration completeness: fail

The sole-authority repair was required to eliminate mirrors without changing the already-accepted certificate acceptance set. It did not fully do so.

At predecessor commit `5f86547a2f16e5f1e1620823e3b68457fb8350b7`, the active field:

```text
spec/rules.yaml#certificate_serialization.duplicate_mapping_keys_policy
```

had value `reject`. The previous closure report expressly accepted this rule as part of P1-01 closure and stated that duplicate keys are rejected before logical checking (`audit/m0/M0_FOUNDATIONAL_SECOND_CLOSURE_RECHECK_2026-09-05.md:107–124`).

The M0.5 canonical tree at `spec/rules.yaml:9–217` has no serialization or mapping-key-uniqueness policy. Neither `identifier_policy`, `top_level`, `node`, the six kind contracts, nor `dag` supplies an equivalent rule. The current nonnormative certificate rendering at `docs/PROOF_CERTIFICATE_SPEC.md:17–70` also omits it.

The remaining strict loader does not repair this omission:

- `scripts/validate_spec.py:96–180` defines and uses `StrictLoader` to load the four **specification** YAML files;
- `tests/spec/test_yaml_loader.py:6–11` tests duplicate-key rejection only through that spec/audit loader;
- no M1 certificate parser exists, and the canonical contract does not require an independent implementation to use this Python helper;
- `AGENTS.md:24–27` affirmatively tells M1 to implement the canonical contract, not removed registries or explanatory material.

Closed-world allowed-field sets do not answer this question. After a permissive parser has collapsed duplicate keys, the resulting map can have exactly the allowed field set. The missing rule is about the byte/document-to-map boundary before closed-world checking.

### 4.3 Independent-implementation question

**Are two independent M1 implementations now forced to accept the same logical certificate documents? No.**

One conforming-looking implementation can reject duplicate YAML/JSON members; another can apply first-key-wins or last-key-wins and then validate the resulting allowed-field map. The sole current authority does not choose among them. If the intended kernel boundary is instead an already-parsed abstract mapping, that too must be stated normatively together with the required document-to-mapping decoder. No such boundary appears in the candidate.

## 5. B — independent replay of all nine formerly accepted mutations

Each probe deep-copied the exact candidate bundle, changed the named field under the actual `canonical_certificate_contract`, and called `validate_bundle(..., freeze=True)`. These were not mirror-only tests.

| # | Canonical-contract mutation | Freeze result | Issue codes |
| ---: | --- | --- | --- |
| 1 | Permit missing postulate-map keys | Rejected | `POSTULATE_SUBSTITUTION`, `FINGERPRINT_CONTRACT` |
| 2 | Use independent definition environments | Rejected | `DF_POLICY`, `FINGERPRINT_CONTRACT` |
| 3 | Permit a second implicit definition conversion | Rejected | `DF_POLICY`, `FINGERPRINT_CONTRACT` |
| 4 | Permit multiple replacements in one `Sb` node | Rejected | `SB_POLICY`, `FINGERPRINT_CONTRACT` |
| 5 | Make `atom.name` traversable | Rejected | `CONTRACT_PATH_TRAVERSAL`, `FINGERPRINT_CONTRACT` |
| 6 | Add node metadata as a logical field | Rejected | `CONTRACT_NODE_FIELDS`, `FINGERPRINT_CONTRACT` |
| 7 | Allow extra node fields | Rejected | `CONTRACT_NODE_POLICY`, `FINGERPRINT_CONTRACT` |
| 8 | Permit string-or-integer parent references | Rejected | `CONTRACT_ID_POLICY`, `FINGERPRINT_CONTRACT` |
| 9 | Make string identity coercive | Rejected | `CONTRACT_ID_POLICY`, `FINGERPRINT_CONTRACT` |

The repository mutation tests do target the sole authority: `tests/spec/test_second_closure_mutations.py:16–19` always passes `rules["canonical_certificate_contract"]` to the mutation, and lines 24–112 cover the nine cases plus an arbitrary extension. This is a genuine improvement over M0.4.

These successful probes establish that the current tree is protected against changes to represented fields. They cannot establish that every required rule was represented before the tree was fingerprinted; the lost duplicate-key policy is exactly such an omission.

## 6. C — whole-contract lock

`audit/m0/certificate_contract_lock.yaml` identifies:

```text
lock_version: 0.1
repair_parent_commit: 5f86547a2f16e5f1e1620823e3b68457fb8350b7
contract_path: spec/rules.yaml#canonical_certificate_contract
contract_version: 1.0
canonical_contract_sha256: 3152eb49a5d268904f0b960faa52b3d57e8b90cd80d14bdbfa8550df012c4d56
```

Independent canonical-JSON serialization and SHA-256 computation produced the same digest. `scripts/validate_spec.py:651–673` checks lock version, repair parent, path, contract version, change-policy text, and the full canonical-tree digest. An unrecognized `unreviewed_semantic_extension` inserted anywhere in that tree produced `FINGERPRINT_CONTRACT`.

The documented limitation is accurate: a deliberate simultaneous contract-and-hash edit is not cryptographically authenticated by the local validator and requires focused independent re-audit (`certificate_contract_lock.yaml:7–9`; `docs/FOUNDATIONAL_SPEC_v0.5.md:118–125`).

The lock is useful but not a correctness oracle. At this commit it faithfully fingerprints a contract from which one accepted serialization rule is absent.

## 7. D — internal contradiction probes

| Probe | Result | Evidence |
| --- | --- | --- |
| Add `primitive_rules` | Rejected | `RULES_TOPLEVEL_KEYS`, `LEGACY_RULES_SEMANTICS` |
| Add `kernel_certificate_kinds` | Rejected | Same |
| Add `occurrence_path_grammar` | Rejected | Same |
| Add `proof_node_grammar` | Rejected | Same |
| Add `dag_invariants` | Rejected | Same |
| Add `certificate_serialization` | Rejected | Same |
| Add `trusted_kernel_invariant` | Rejected | Same |
| Add executable `constraints` to `lewis_operations.Sa` | Rejected | `LEWIS_OPERATION_FIELDS` |
| Add an unrecognized semantic extension inside the canonical tree | Rejected | `FINGERPRINT_CONTRACT` |

Thus the requested contradiction-injection checks pass. The certification failure is different: a required policy was removed before the one remaining representation was locked.

## 8. E — validators, tests, hygiene, and exact-SHA CI

### 8.1 Local commands

| Command | Result |
| --- | --- |
| `python scripts/validate_spec.py` | PASS; version 0.5, 7 constructors, 12 schemas, 4 Lewis operations, 6 certificate kinds, 5 systems |
| `python scripts/validate_source_register.py` | PASS |
| `python scripts/validate_spec.py --freeze` | PASS |
| `python scripts/validate_source_register.py --freeze` | PASS |
| `pytest` | PASS; `32 passed in 1.16s` after installing the repository-declared `pytest>=8,<9` dev dependency in the transient runner |
| `git ls-files '*:Zone.Identifier'` | PASS; exit 0 with no output |

The detached candidate remained clean after testing.

### 8.2 Exact-SHA GitHub Actions

GitHub Actions run [33944328957](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/33944328957) is a completed successful `push` run whose `head_sha` is exactly `5436a3d2a8a7eecefc26712c2505f1b271c4c200`. Its sole job, `validate-m0-spec`, succeeded, including dependency installation, `Zone.Identifier` rejection, both ordinary validators, both freeze validators, and the pytest step.

The workflow at `.github/workflows/m0-spec-validation.yml:3–29` covers all governing M0 paths, and lines 51–72 run the hygiene check, four validators, and tests.

### 8.3 What green validation establishes—and does not establish

The gates establish structural conformance to the current canonical tree and exact identity with its stored digest. They do not prove that the new tree preserved every semantic leaf of the removed registries. The duplicate-key omission passes because:

1. no current expected-contract constant requires such a field;
2. the whole-contract hash was calculated after the omission;
3. the duplicate-key unit test exercises only the specification loader.

Therefore green CI does not close the new P1.

## 9. F — non-regression

Direct comparison used parsed YAML objects from candidate `5436a3d2…` and parent `5f86547a…`, not display strings or line-oriented similarity.

### 9.1 Formula and definition locks

- All 12 stored schema ASTs (`B1–B8`, `A8`, `C10–C12`) are exactly equal.
- All three definition `{lhs,rhs}` objects (`DEF_OR`, `DEF_STRICT_IMP`, `DEF_EQUIV_S`) are exactly equal.
- `audit/m0/certified_ast_fingerprints.yaml` is unchanged from the parent.
- The only diffs in `spec/language.yaml`, `spec/schemas.yaml`, and `spec/systems.yaml` are `spec_version: '0.4'` to `'0.5'`.
- `python scripts/validate_spec.py --freeze` independently recomputed all 15 protected hashes successfully.

No formula/source regression occurred, so no B1–C12 or historical-page re-audit is required.

### 9.2 Normalized basis membership

| Basis ID | Resolved schema set | Parent comparison |
| --- | --- | --- |
| `S1_B1_B7` | `B1–B7` | Exact |
| `S2_B1_B8` | `B1–B8` | Exact |
| `S3_B1_B7_A8` | `B1–B7 + A8` | Exact |
| `S4_B1_B7_C10` | `B1–B7 + C10` | Exact |
| `S5_PRIMARY_B1_B7_C11` | `B1–B7 + C11` | Exact |
| `S5_ALT_B1_B7_C10_C12` | `B1–B7 + C10 + C12` | Exact |

### 9.3 S5 bridge orientation

The complete two bridge-obligation objects are exactly equal to the parent:

| Translation | `from_basis_id` | `into_basis_id` | Must derive | Expanded certificate basis |
| --- | --- | --- | --- | --- |
| Primary → alternative | `S5_PRIMARY_B1_B7_C11` | `S5_ALT_B1_B7_C10_C12` | `C11` | Alternative |
| Alternative → primary | `S5_ALT_B1_B7_C10_C12` | `S5_PRIMARY_B1_B7_C11` | `C10`, `C12` | Primary |

There is no union basis and no bridge-direction regression.

## 10. Full defect register

| ID | Severity | Disposition |
| --- | --- | --- |
| M0.5-P1-01 | **P1** | Open — duplicate certificate mapping-key policy was lost during single-authority migration. |
| M0.5-P2-01 | **P2** | Open — validator/tests and closure records do not detect the P1 semantic loss and therefore overstate freeze readiness. |
| P0 | — | None. |
| P3 | — | None required for certification. |

### M0.5-P1-01 — duplicate-key rejection absent from the sole certificate authority

1. **Exact file/location:** `spec/rules.yaml:9–217`, where the complete sole `canonical_certificate_contract` is defined but contains no duplicate-key policy. The removed predecessor rule was `5f86547a…:spec/rules.yaml#certificate_serialization.duplicate_mapping_keys_policy = reject`. `AGENTS.md:24–27` makes the canonical tree exclusively controlling. `docs/PROOF_CERTIFICATE_SPEC.md:17–70` also no longer renders the rule.
2. **Exact defect:** M0.5 removed the legacy `certificate_serialization` registry without migrating its `duplicate_mapping_keys_policy: reject` invariant into the sole contract or defining an equivalent strict document-decoding boundary.
3. **Why it matters:** different conforming-looking parsers can reject, keep the first value, or keep the last value for duplicate keys. Closed-world field validation occurs only after that choice. A duplicate `root`, `nodes`, `goal`, `basis_id`, `conclusion`, or justification field can therefore yield different accepted proof documents and potentially different checked formulas. Independent M1 implementations are not forced to agree.
4. **Required repair:** put one exact duplicate-mapping-key rejection rule inside `canonical_certificate_contract`; normatively define the accepted document encoding/decoding boundary; require rejection before logical checking; make `validate_spec.py` assert the canonical field; add both a direct canonical-policy mutation test and a certificate-document duplicate-key rejection fixture; update the nonnormative rendering and closure records; recompute the whole-contract lock.
5. **Changes intended calculus?** No. It restores the M0.4 certificate serialization rule already accepted by the preceding audit. It changes no formula, definition, Lewis operation, system basis, or bridge.
6. **Re-audit dependency:** one focused exact-SHA certificate-boundary recheck covering the new canonical field, strict document decoding, mutation rejection, updated lock, all validators/tests, and CI. No historical source or formula audit is needed if AST/basis fingerprints remain unchanged.

### M0.5-P2-01 — the freeze gate locks the omission and the duplicate-key test covers the wrong boundary

1. **Exact file/location:** `scripts/validate_spec.py:65–94,318–508` has no expected canonical duplicate-key field; `scripts/validate_spec.py:651–673` hashes the incomplete tree; `tests/spec/test_yaml_loader.py:6–11` checks the spec loader rather than a proof-certificate boundary; `audit/m0/foundational_obligations.yaml:288–297` keeps M0-C05 marked `closed`; `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.5.md:68–87,110–123` claims whole-contract protection/non-regression without identifying this loss.
2. **Exact defect:** all automated checks pass when the sole authority lacks a previously required certificate-serialization invariant. The lock establishes identity only after the omission.
3. **Why it matters:** the candidate's green freeze result and closed M0-C05 status overstate certificate-boundary completeness and would permit an unsafe freeze.
4. **Required repair:** couple the P1 repair to an explicit validator assertion; mutate that exact canonical field in freeze tests; add an end-to-end duplicate certificate-key rejection test or a normative parser conformance fixture; reopen M0-C05 until the focused recheck closes it.
5. **Changes intended calculus?** No; validation and audit-accounting only.
6. **Re-audit dependency:** the same focused exact-SHA recheck as M0.5-P1-01.

## 11. Minimal repair plan

1. Add a single normative serialization/decoding subobject inside `canonical_certificate_contract` specifying that mapping keys must be unique and duplicates are rejected before construction of the logical certificate map. Do not reintroduce `certificate_serialization` as a top-level mirror.
2. Specify which serialized certificate formats M1 may accept, or define one canonical decoding interface. Every allowed decoder must reject duplicate keys before logical validation.
3. Extend `_check_rules` to require the exact policy and retain the whole-contract fingerprint as defense in depth.
4. Add a mutation changing the policy from `reject` to an accepting behavior and require freeze failure. Add a duplicate `root`/justification key document fixture demonstrating parser-level rejection.
5. Update `PROOF_CERTIFICATE_SPEC.md`, M0-C05, the repair log, and the contract lock; rerun all gates and exact-SHA CI.
6. Perform one narrow closure recheck. Do not redo formula/source work unless a protected AST or basis changes.

## 12. Final recommendation

The M0.5 work correctly establishes a single active representation and fixes the nine demonstrated freeze-gate holes, but it does not preserve the complete accepted certificate serialization contract. Because one P1 remains and independent M1 implementations can disagree on duplicate-key documents, commit `5436a3d2a8a7eecefc26712c2505f1b271c4c200` must **not** be frozen as M0.

**M1 trusted-kernel implementation may not begin.** Apply the minimal serialization-boundary repair and conduct one further narrow exact-SHA recheck.
