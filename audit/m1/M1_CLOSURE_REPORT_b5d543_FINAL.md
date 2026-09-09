M1 TRUSTED KERNEL NOT CERTIFIED

# Focused M1 closure report

Repository: `Raycaesar/lewis-strict-implication-prover`\
Candidate: `b5d543db60ed7631f9e182f137ce2f83156d2ec3`\
Report completed: 2026-09-09 UTC; verification evidence collected on 2026-09-08 UTC.

## 1. Overall verdict

**One P0 remains: the public Python checking API accepts specification objects whose frozen-M0 integrity has not been established.** Completed independent checks demonstrated false certificate acceptance through this boundary in definition conversion and primitive-basis admission.

The file-loader repair works. Frozen M0 is unchanged, all 69 independent temporary specification mutations were rejected, valid behavior remained intact under the genuine specification, all 1,095 repository tests passed, and both exact-SHA CI workflows succeeded. The two previous P2 findings are closed.

These positive results do not establish the required acceptance equivalence across the declared trusted Python API. Certification remains blocked.

This report completes the interrupted recheck using existing evidence. No tests were rerun on resumption, no repairs were implemented, and no audited repository files were modified. Temporary fixtures, audit scripts and report files are outside the candidate and are not evidence of a repaired committed implementation.

## 2. Exact repaired SHA/tree/CI identity

| Identity | Verified value |
| --- | --- |
| Candidate commit | `b5d543db60ed7631f9e182f137ce2f83156d2ec3` |
| Candidate tree | `246b50830712b2c8709cda2566c90d4273498375` |
| Direct parent | `d87f1145da766f4ccbb7a9f9b76e9d15328d50da` |
| Audit checkout | Detached at the exact candidate; clean at the completed verification checkpoint. |
| M1 Actions run/job | `34262651728` / `102184197541`: completed, success. |
| M0 Actions run/job | `34262651681` / `102184197245`: completed, success. |

Both workflow runs identify the exact candidate as `head_sha`. Their jobs, steps and execution logs were inspected; no later branch run was substituted. [M1 run](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/34262651728), [M0 run](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/34262651681).

On resumption, the original shared Git metadata was unavailable. The recorded exact-SHA, tree, clean-status and test evidence remained available and was used without reconstructing the checkout or repeating the audit. The certification decision concerns only the committed candidate identified above.

## 3. Certified-M0 and administrative-freeze lineage

| Stage | Commit | Verified relation |
| --- | --- | --- |
| Certified M0 candidate | `21117f3da827f873c3ed88b578a1681aabfca7ac` | Exact candidate certified by the stored final M0 report. |
| Pure administrative freeze | `33e6a14a4b92534ea159868060576d1b45da9bb5` | Direct child of certified M0. |
| M1 implementation replay | `d87f1145da766f4ccbb7a9f9b76e9d15328d50da` | Direct child of the administrative freeze. |
| Repaired M1 candidate | `b5d543db60ed7631f9e182f137ce2f83156d2ec3` | Direct child of the replay. |

The certified M0 tree is `25b2e20af085625285c6f8bd6ab5a1b1c5b66a09`; the administrative-freeze tree is `1c5018a1e1fa9c7f771de3fd952f51b82bd35f2b`.

The historical failed candidate `e0837632aa9e187ccbc5a6fcc1a3a8816e17fe56` remains on the older lineage through report-only commit `3ded752aef28be17509649fbcd47a3daf29c7279`. It is not an ancestor of the repair. Its complete tree and the replay tree are exactly equal: `2f26744cb63d50a23a218c545ffedc6f83652ef3`.

This establishes the permitted reconstruction: an independently reviewable administrative freeze, an exact replay of the failed implementation, and a separate repair. Both M1 commits on the repaired lineage descend from the proper freeze baseline.

## 4. Frozen-M0 non-regression result

Independent comparison passed 21 provenance/non-regression assertions, including equality of 36 protected parsed objects across certified M0, the historical report-only state, administrative freeze, failed M1, replay and repair.

| Protected object | Result |
| --- | --- |
| Four complete specification documents, excluding only root administrative status | Exactly equal. |
| Seven complete formula-constructor declarations | 7/7 exactly equal. |
| B1–B8, A8, C10–C12 schema ASTs | 12/12 exactly equal. |
| DEF_OR, DEF_STRICT_IMP, DEF_EQUIV_S LHS/RHS pairs | 3/3 exactly equal. |
| Six normalized basis blocks, including both S5 identities | 6/6 exactly equal. |
| Complete S5 bridge records | Exactly equal. |
| Entire canonical certificate contract | Exactly equal. |
| Both complete M0 lock objects | Exactly equal; byte-identical to certified M0. |

All six runtime input files are byte-identical from administrative freeze through repaired M1. The manifest digests were independently matched to the administrative freeze's Git blobs, not inferred from the repair log.

The canonical contract retains digest `c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316`. No unauthorized M0 semantic change was found. Historical Lewis source research therefore did not require reopening.

## 5. Previous P0 loader repair result

The previous defect arose because [transforms.py][transforms], in `_match` and `_instantiate`, consumed constructor child-field declarations that the old loader did not authenticate. Locking the schema and definition ASTs did not fix how those ASTs were interpreted.

The repaired [load_frozen_spec][loader] validates complete file identity, including every constructor declaration, before returning trusted executable structures. The added manifest contains provenance identities and digests; it does not introduce a second formula or certificate semantics registry.

**The file-loading defect is closed. The broader trusted-input invariant remains open because public Python entry points do not require an authenticated specification object.**

## 6. File-loader integrity closure

The checker-owned [frozen_baseline.py][manifest] pins these complete runtime inputs to the administrative freeze:

- `spec/language.yaml`;
- `spec/rules.yaml`;
- `spec/schemas.yaml`;
- `spec/systems.yaml`;
- `audit/m0/certified_ast_fingerprints.yaml`;
- `audit/m0/certificate_contract_lock.yaml`.

The loader reads each file once and uses the same byte snapshot for parsing and hashing. Existing metadata, AST, contract and basis checks remain active. Raw integrity validation precedes trusted basis construction, recursive freezing and the returned `FrozenSpec`. No theorem checking occurs during preflight.

| Integrity property | Result |
| --- | --- |
| Digests correspond to the correct administrative freeze | Verified. |
| Every file read by the production frozen loader is covered | Verified: all six inputs. |
| Constructor membership, fields/order, arity, classification and definition linkage protected | Verified by complete-file identity. |
| Occurrence grammar and rule/certificate contract protected | Verified by whole-contract and complete-file checks. |
| Mismatch fails before trusted structures are returned | Verified. |
| Parsing and hashing use one captured input snapshot | Verified. |
| Caller-selected directory can supply its own integrity manifest | No such production path found. |
| Runtime baseline regeneration, alternate loader or permissive fallback | None found. |
| Genuine returned mappings and digest registry are ordinarily immutable | Verified. |

The production CLI invokes this loader before reading the certificate. Valid input returns exit 0 and `VALID_CERTIFICATE`; logical and document failures return exit 1 with distinct error identities; frozen-spec mismatch returns exit 2 with `frozen_spec_error`. The former file-based false acceptance is no longer reachable through that CLI sequence.

This protection is conditional on entering through the loader. It does not authenticate independently supplied `FrozenSpec` values at the Python checking boundary.

## 7. Temporary specification mutation results

All mutations used local temporary copies outside the audited worktree. Changes were checked against the real production loader.

| Independent mutation class | Cases | Expected result | Actual result |
| --- | ---: | --- | --- |
| Seven constructor field/child declarations | 7 | Loader rejection | 7 rejected. |
| Constructor arity | 7 | Loader rejection | 7 rejected. |
| Primitive classification | 7 | Loader rejection | 7 rejected. |
| Object-level classification | 7 | Loader rejection | 7 rejected. |
| Binary child ordering | 4 | Loader rejection | 4 rejected. |
| Defined-constructor definition association | 3 | Loader rejection | 3 rejected. |
| Defined-constructor surface status | 3 | Loader rejection | 3 rejected. |
| Seven occurrence child declarations | 7 | Loader rejection | 7 rejected. |
| Path segments, root path, traversal expansion and Sb root policy | 4 | Loader rejection | 4 rejected. |
| Schema AST, definition AST, contract field, contract digest and AST lock | 5 | Loader rejection | 5 rejected. |
| Basis ID, membership and S5 union policy | 3 | Loader rejection | 3 rejected. |
| Parser precedence and associativity declarations | 2 | Loader rejection | 2 rejected. |
| Four frozen component statuses | 4 | Loader rejection | 4 rejected. |
| Additional byte change in each complete frozen input file | 6 | Loader rejection | 6 rejected. |
| **Total** | **69** | **Rejection before theorem checking** | **69/69 conforming.** |

Constructor and raw-file differences raised `FrozenSpecIntegrityError`; retained semantic checks produced their corresponding typed frozen-spec errors. No tested altered file bundle yielded a trusted specification.

## 8. Definition-conversion regression result

With the genuine frozen specification, independent checks confirmed:

- all three registered definitions in both directions, at root and nested occurrences;
- one shared metavariable environment and structural consistency of repeated occurrences;
- exactly one selected replacement;
- rejection of incorrect definition identity, direction, path, multiple-occurrence change and implicit additional conversion.

Twelve direct transformation cases and eight independently assembled complete conversion certificates passed. The complete positive fixture also remained accepted on a byte-identical copied baseline.

A minimal two-node local DAG in the former defect class was rejected with `invalid_definition_conversion` under genuine M0. Its altered file-based specification was rejected by the repaired loader before certificate checking.

**The same invalid serialized DAG was nevertheless accepted through the direct Python API when supplied an unverified specification model.** This establishes false certificate acceptance; it does not depend on whether the conclusion might have another valid derivation.

Focused occurrence, Sb, schema-instantiation, Sa and Smp checks also preserved their intended behavior under genuine M0, including surface equality, one-occurrence replacement and simultaneous one-pass substitution. Their preserved behavior does not authenticate specification objects supplied through another entry path.

## 9. Basis-discipline regression result

The frozen primitive bases remain:

| Basis | Primitive schemas |
| --- | --- |
| S1_B1_B7 | B1–B7 |
| S2_B1_B8 | B1–B8 |
| S3_B1_B7_A8 | B1–B7 + A8 |
| S4_B1_B7_C10 | B1–B7 + C10 |
| S5_PRIMARY_B1_B7_C11 | B1–B7 + C11 |
| S5_ALT_B1_B7_C10_C12 | B1–B7 + C10 + C12 |

All ten required independent admission probes matched frozen M0: B8 in S1 and A8 in S2 rejected; A8 in S3 and C10 in S4 accepted; C11 was admitted only in S5 primary; C10/C12 were admitted only in S5 alternative. An invented S5 union basis rejected.

The direct Python specification-input check separately demonstrated acceptance of a one-node B8 postulate certificate declared under S1 when supplied an unverified derived basis mapping. That certificate is not licensed as a primitive instance in the declared frozen basis. The systems specification itself remains unchanged.

## 10. Python API trust-boundary audit

[FrozenSpec][model] and `FrozenBasis` are publicly exposed data classes. Their ordinary construction does not establish frozen integrity. The `FrozenSpec` declaration also does not recursively freeze mappings supplied by a caller.

[check_certificate][dag] consumes the supplied specification directly. [NodeChecker.__init__][checker] stores it without verifying loader provenance or equivalent frozen semantic identity. Specification-dependent matching and basis lookup subsequently use that object.

| Completed local API observation | Required behavior | Actual behavior |
| --- | --- | --- |
| Invalid conversion with an immutable, unverified specification model | Reject unverified specification before logical acceptance | Complete certificate accepted. |
| Same derivation through incremental checking | Reject unverified specification | Invalid conversion node accepted. |
| Inconsistent schema matching under that model | Reject unverified specification | Match accepted. |
| B8-in-S1 certificate with an unverified derived basis | Reject unverified specification | Complete certificate accepted. |
| Constructed specification retaining caller-owned mutable semantics | Prevent unauthenticated semantic changes from influencing checking | An unchanged invalid certificate changed from rejection to acceptance. |

These were ordinary local API/model conformance checks. No production source, manifest, private acceptance ledger or interpreter internals were modified. An immutable unverified model alone sufficed for false acceptance; the finding does not depend on modifying a loader-produced object.

The documented instruction that the specification must originate from `load_frozen_spec` is an unenforced caller precondition. Under the requested trusted-API scope, that is insufficient: accepted specification objects must satisfy the frozen-integrity invariant by construction or by enforced validation.

## 11. Remaining Python API P0, confirmed

**Confirmed: M1-CLOSE-01 is P0.** Production-reachable trusted checking can accept serialized certificates not licensed by frozen M0 when its specification argument lacks validated provenance.

The violated invariant is:

> Every acceptance-sensitive specification object reaching trusted checking must have passed frozen-M0 integrity validation.

The established consequences include incorrect definition conversion and primitive admission outside the declared frozen basis. These are two manifestations of the same missing specification-authentication invariant, not changes to the frozen calculus.

The protected CLI, working file loader, green test suite and successful CI do not reduce the severity. False certificate acceptance is already established within the declared Python API surface.

## 12. Administrative-freeze P2 closure

**Closed for the repaired candidate.** The distinct administrative freeze directly descends from certified M0, stores the final certification report, and contains the authorized status/accounting transition without M1 implementation.

Inspection confirmed the four specification statuses, source-register frozen/closed statuses, and closure of `M0-C05`, `M0-C06`, `M0-V04` and `M0-FP04` with certification evidence. The 14 changed administrative file versions match the previously authorized transition. Protected semantic objects are unchanged.

The exact implementation replay and separate repair descend from that baseline. This establishes valid reconstructed provenance without retrospectively changing the old failed branch's history.

## 13. CI path-coverage P2 closure

**Closed.** The dedicated [M1 workflow][workflow] covers push and pull-request changes to every required surface:

`src/lewis_prover/**`, `tests/**`, `scripts/**`, `spec/**`, `audit/m0/**`, `audit/m1/**`, `pyproject.toml`, `AGENTS.md` and `.github/workflows/**`.

No branch filter excludes the repaired M1 lineage. The workflow performs M0 validation, complete pytest execution, frozen-baseline/provenance verification, production CLI smoke checks and whitespace checks. Full Git history is available for provenance validation. No separate uncovered CLI entry-point configuration was found.

The exact-candidate run completed these gates successfully. The remaining API defect is a missing conformance test and production invariant, not the previously reported path-filter failure.

## 14. Full-suite and exact-SHA CI results

| Local measurement | Completed result |
| --- | --- |
| Tests collected/executed | 1,095 |
| Passed | 1,095 |
| Failed / errors / skipped | 0 / 0 / 0 |
| Pytest runtime | 16.79 seconds |
| Pytest warnings | None reported. |
| Runtime | Python 3.12.13, pytest 8.4.2, PyYAML 6.0.3. |
| Previous tests preserved | All 958; every original Python test file unchanged. |
| Added tests | 108 frozen-input tests and 29 CI-coverage tests. |

All four local M0 validation gates, the repository provenance verifier and all nine production CLI smoke checks passed. Whitespace checks passed and no tracked `Zone.Identifier` file was present. The worktree was clean at the completed verification checkpoint.

The exact-SHA M1 workflow recorded 1,095 passes in 21.67 seconds and again in 21.28 seconds, successful provenance verification and all nine CLI smoke checks. The exact-SHA M0 workflow recorded 1,095 passes in 12.76 seconds, with its frozen validation and tracked-metadata checks successful. CI used Python 3.12.14, pytest 8.4.2 and PyYAML 6.0.3. Setup emitted Node.js deprecation notices; test runs reported no warnings or failures. [M1 evidence](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/34262651728), [M0 evidence](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/34262651681).

The independent focused record contains 158 observations: 153 expected outcomes and five observations of the API-origin failure described above. This is one remaining P0 supported by several checks; a standalone schema-match result is not itself whole-proof acceptance.

The new regression tests exercise the actual loader and transformations, but they obtain their specification through the loader before calling the operation being tested. They therefore do not detect the independently supplied `FrozenSpec` boundary. The complete suite was not rerun after resumption.

## 15. Complete remaining P0–P3 defect register

| Required field | M1-CLOSE-01 |
| --- | --- |
| ID | **M1-CLOSE-01** |
| Severity | **P0** |
| Violated invariant | Every acceptance-sensitive runtime specification object must represent authenticated frozen M0 before checking. Complete registered definition matching and exact primitive-basis admission must follow that authority. |
| Affected file/function/API boundary | [kernel/model.py][model]: `FrozenSpec`, `FrozenBasis`; [kernel/dag.py][dag]: `check_certificate`; [kernel/checker.py][checker]: `NodeChecker.__init__`, `check_node`. Affected consumers include [transforms.py][transforms] `_match`/`_instantiate` and [basis.py][basis] `validate_basis`. |
| Conformance | **Nonconforming** at the public Python specification-input boundary. |
| Actual behavior | Caller-constructed specification data can determine trusted matching and basis admission without establishing frozen integrity. Complete invalid certificates were accepted. |
| Required behavior | Authenticate the specification and all derived acceptance-sensitive data, or reject the object, before logical checking. |
| Formal counterexample description | A two-node S1 DAG contains a valid B5 instance followed by a claimed DEF_EQUIV_S contraction lacking the required reverse implication. Genuine M0 rejects it; the unverified-specification API path accepts it. A separate one-node B8-in-S1 instance establishes the same boundary failure for primitive admission. |
| False acceptance / false rejection | **False acceptance confirmed.** No new false rejection was observed with the genuine validated frozen specification. |
| Current repository tests detect it? | **No.** All 1,095 pass; the new loader tests do not enforce provenance at direct model-input entry points. |
| Minimum repair boundary | Enforce an authenticated, recursively immutable validated-specification boundary for every public trusted checking path, including derived bases and specification-dependent transformations. Arbitrary construction or reconstruction must not confer trusted status. |
| M1-only? | **Yes.** Preserve frozen M0, both lock objects and their digests. |
| Certification blocked? | **Yes.** |

| Severity | Remaining independent defects |
| --- | ---: |
| P0 | 1 |
| P1 | 0 identified. |
| P2 | 0 remaining; both previous P2 findings closed. |
| P3 | 0 recorded. |

The test-coverage and documentation qualifications concerning this public input boundary belong to M1-CLOSE-01's closure work. They are not counted as separate instances of the same root cause.

## 16. Minimum M1-only repair boundary

**Yes: the required architectural repair is to prevent trusted checker entry points from accepting arbitrary caller-constructed `FrozenSpec` objects unless frozen provenance and integrity have been established by the trusted loader or an equivalent unforgeable validated-spec boundary.**

That boundary must cover the complete semantic contents and derived basis data, preserve recursive immutability, and apply consistently to whole-certificate checking, incremental checking and exposed trusted specification-dependent operations. Trusted status must not follow merely from a class name, caller assertion or copied validation marker.

The minimum closure work is:

1. Enforce that validated-spec invariant in production M1, preserving the existing file-integrity mechanism and frozen M0 authority.
2. Add regression coverage for ordinary direct/reconstructed specification values and retained mutable aliases, including invalid-conversion and wrong-basis controls. Retain valid loader-produced and byte-identical copied-baseline behavior.
3. Correct the implementation log and integrity inventory where complete API protection was inferred from loader-only tests.
4. Re-audit that boundary and its affected consumers on a new immutable candidate, with focused conformance evidence, the complete suite and successful exact-SHA CI.

No M0 semantic revision, historical-source re-audit or unrelated refactoring is required. This report supplies no repaired implementation.

## 17. Certification decision

The committed candidate does not satisfy:

> Accepted by production M1 if and only if licensed by frozen M0, within the declared trusted M1 API surface.

A reproducible false acceptance remains at the public Python API boundary. The evidence does not establish that this boundary preserves frozen-M0 acceptance; it establishes that it can enlarge it.

**M1 at `b5d543db60ed7631f9e182f137ce2f83156d2ec3` cannot be certified.** Temporary audit artifacts and report-generation changes do not alter that decision or the candidate tree.

## 18. M2 recommendation

**M2 MUST NOT BEGIN.**

The remaining P0 must be repaired in M1 and independently closed before M2 historical/native proof regression is authorized.

[loader]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/frozen_spec.py
[manifest]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/frozen_baseline.py
[model]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/model.py
[transforms]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/transforms.py
[dag]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/dag.py
[checker]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/checker.py
[basis]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/src/lewis_prover/kernel/basis.py
[workflow]: sandbox:/workspace/scratch/a2d5d54170cf/m1-closure-b5d543/.github/workflows/m1-trusted-kernel-validation.yml
