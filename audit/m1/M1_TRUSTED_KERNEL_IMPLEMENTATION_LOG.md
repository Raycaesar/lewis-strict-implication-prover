# M1 Trusted Kernel Implementation and Audit Repair Log

Repair verification: 2026-09-09 (Asia/Shanghai; 2026-09-08 UTC).
Repository: `Raycaesar/lewis-strict-implication-prover`.

The independent Work Max audit of the failed M1 commit returned
**M1 TRUSTED KERNEL NOT CERTIFIED**. This document records repairs to its one
P0 and two P2 findings and the resulting local validation. It does not claim
M1 certification. M2 and proof search remain unimplemented.

## 1. Exact provenance and reconstructed history

| Identity | SHA / value |
| --- | --- |
| Certified M0 candidate | `21117f3da827f873c3ed88b578a1681aabfca7ac` |
| Historical report-only commit / unchanged tag `m0-foundational-spec-v1` | `3ded752aef28be17509649fbcd47a3daf29c7279` |
| Pure administrative M0 freeze, reconstructed locally | `33e6a14a4b92534ea159868060576d1b45da9bb5` |
| M1 implementation baseline, exact tree replay on that freeze | `d87f1145da766f4ccbb7a9f9b76e9d15328d50da` |
| Audited failed M1 SHA | `e0837632aa9e187ccbc5a6fcc1a3a8816e17fe56` |
| Repaired M1 candidate | `PENDING_FINAL_COMMIT` |
| Local repair branch | `m1/work-max-audit-repair` |

The repaired-candidate field is pending because this log is included in that
commit and cannot contain its own Git hash. The enclosing repair commit is
the candidate; the final delivery records its exact SHA. `d87f114` is only the
failed implementation replay and is not the repaired candidate.

The M0 certification authority is the existing report
[`M0_FOUNDATIONAL_M0_6_DUPLICATE_KEY_CLOSURE_RECHECK_2026-09-05.md`](../m0/M0_FOUNDATIONAL_M0_6_DUPLICATE_KEY_CLOSURE_RECHECK_2026-09-05.md).
It certifies exact candidate `21117f3`, and section 12 authorizes the
administrative status/accounting transition. The old `3ded752` commit added
only that report, so its title/tag did not satisfy the administrative gate.
The required changes were originally bundled with implementation in `e083763`.

On a new branch directly from `21117f3`, the repair created `33e6a14` containing
only the already authorized transition: the existing certification report;
four root statuses `candidate_m0 -> frozen_m0`; source-register freeze/closure
statuses; closure of M0-C05, M0-C06, M0-V04 and M0-FP04 with report evidence;
and the existing administrative checklist/documentation/accounting updates.
All 14 administrative file versions equal their previously authorized versions
in `e083763`. There is no M1 source, M1 test, or M1 log in this freeze commit.

All four M0 validation gates and the original 44 M0 tests passed on that pure
freeze before committing it (`44 passed in 0.49s`). This is a reconstruction
of reviewable ordering; it does not change the provenance defect in the old
branch. The freeze checklist's historical exact-SHA Actions evidence belongs
to certified candidate `21117f3`, as identified in its audit report. No hosted
CI run is claimed for the reconstructed freeze or this local repair.

The original implementation was then replayed onto `33e6a14`. Both `d87f114`
and failed `e083763` have tree
`2f26744cb63d50a23a218c545ffedc6f83652ef3`. The replay retains the full source
state, tests, fixtures, packaging, and historical log, including the known
failed behavior. The earlier detailed implementation record remains available
in that replay commit. The present repair is a separate subsequent commit.

```text
21117f3  certified M0 candidate
  -> 33e6a14  pure administrative M0 freeze
    -> d87f114  exact M1 implementation replay (known failed baseline)
      -> PENDING_FINAL_COMMIT  M1 P0/P2 audit repair candidate
```

`main`, `origin/main`, and the historical M0 tag are preserved. No push,
force-push, remote branch update, tag movement, or audit submission was made.

## 2. Work Max findings and exact repair

| Severity | Audited finding | Repair |
| --- | --- | --- |
| P0 | Formula-constructor declarations used by trusted transformations escaped frozen integrity checks; temporary spec changes could alter acceptance while old locks still passed. | Checker-owned manifest pins all six complete input files to the administrative freeze. A mandatory raw-byte integrity gate runs before any trusted basis or FrozenSpec is constructed. |
| P2 | No separately reviewable administrative M0 freeze preceding M1 implementation. | New local branch reconstructs a pure freeze directly on certified M0, followed by the byte-identical M1 replay and this separate repair. |
| P2 | CI path filters omitted M1 production and test surfaces. | Dedicated M1 workflow covers all requested paths for push and pull_request, with full M0/M1 checks, provenance validation, CLI smoke checks, and whitespace checks. |

### Root cause and confirmed reproducer

The old loader pinned schema/definition AST hashes, the complete certificate
contract, lock objects, metadata, and resolved bases. It did not authenticate
`language.formula_ast`. `transforms._match` and `_instantiate` read the mutable
constructor `fields` lists from that unvalidated object. AST immutability and
contract hashing therefore did not guarantee unchanged interpretation of the
ASTs by trusted transformations.

Before changing production code, the exact replay reproduced the defect using
only a copied spec with `formula_ast.and.fields: [left]`. A valid B5 instance
`p ⥽ ∼∼p` was adjoined to itself. Invalid contraction of that conjunction to
`p ≡ₛ ∼∼p` was then accepted: `_match` skipped the second implication and never
required the reverse implication. The ordinary frozen spec rejected the same
serialized certificate at `invalid_definition_conversion`, node `root`,
detail `DEFINITION_CONVERSION`. Both original locks remained valid under the
mutation. This is an invalid derivation being accepted, regardless of whether
its conclusion has some other proof.

The same copied-spec mutation made B1 falsely match
`(p ∧ q) ⥽ (q ∧ r)`: traversal skipped the right children that would expose
an inconsistent repeated metavariable. `_instantiate` consumes the same
unchecked fields; missing fields can cause constructor failures, also now
rejected at the loader boundary. No broader false-acceptance claim is inferred
from those instantiation failures.

### Complete input boundary

`src/lewis_prover/kernel/frozen_baseline.py` contains only provenance SHA
identities and SHA-256 digests of these raw Git blobs at `33e6a14`:

```text
spec/language.yaml
spec/rules.yaml
spec/schemas.yaml
spec/systems.yaml
audit/m0/certified_ast_fingerprints.yaml
audit/m0/certificate_contract_lock.yaml
```

There are no formula, definition, rule, or traversal semantics in the manifest.
The existing YAML authorities remain the sole executable specification. The
manifest ships with the checker; a temporary `--spec-root` cannot supply a
replacement. Production initialization requires neither Git nor `audit/m1`.

The loader reads each file once, parses the same byte snapshot with the
existing unique-key YAML loader, preserves the existing metadata/AST/contract/
basis validation diagnostics, and verifies every raw digest. Basis preflight
now validates data without creating `FrozenBasis`. Only after all checks pass
does `_build_bases` construct trusted bases and the loader recursively freeze
and return `FrozenSpec`. No trusted transform or theorem check runs during
preflight. The parser never rereads disk after hashing. Two tests change the
file after its one read, in both directions, and verify that parsed and hashed
content cannot diverge.

Whole-file identity covers all seven constructor declarations, including exact
arity, field list membership/order, primitive classification, object level,
surface status, and definition association. It also covers all other fields
in every consumed file. Byte-different copies, including comment-only edits,
are outside this exact frozen baseline and reject. Ordinary byte-identical
copies retain valid behavior. Existing semantic fingerprint, contract, unique
YAML-key, status, and basis checks remain active as defense in depth, with
all their original tests and diagnostic assertions unchanged.

### Inventory and transform impact

The explicit field/consumer/acceptance-sensitivity/before-and-after-validation
inventory is
[`FROZEN_SPEC_INTEGRITY_INVENTORY.md`](FROZEN_SPEC_INTEGRITY_INVENTORY.md).
It includes every dynamic spec read under kernel and syntax, fixed-code
consumers, diagnostic-only definition associations, and immutable derived
basis consumers.

Occurrence resolution/rebuilding, Sa atom collection/substitution, and direct
Sb replacement use `contract.occurrence_path.traversable_fields`, which was
already protected by the whole-contract lock. The language-only P0 mutation
does not independently redirect those traversals. Sb and other rule nodes can
consume an invalid ancestor accepted through definition conversion, however.
New tests cover that downstream use through Sb, Sa, Ad, and Smp. Schema
matching and conversion are directly affected; schema instantiation shares
the unchecked dependency. Diagnostic erasure reads constructor-definition
links but is outside certificate acceptance. All these input paths now require
the complete frozen baseline; no transform semantics were changed.

## 3. Files changed by this repair (relative to d87f114)

| File | Change |
| --- | --- |
| `src/lewis_prover/kernel/frozen_baseline.py` | Six-file integrity manifest and certified/freeze provenance identities |
| `src/lewis_prover/kernel/frozen_spec.py` | Single-read snapshots, whole-file integrity gate, and trusted-basis construction after validation |
| `src/lewis_prover/errors.py` | Typed `FrozenSpecIntegrityError` |
| `tests/kernel/test_frozen_baseline.py` | 108 loader, constructor, transform, downstream-certificate, and CLI-boundary regression cases |
| `tests/m1/test_ci_coverage.py` | 29 push/PR path and mandatory-command coverage cases |
| `tests/fixtures/m1/invalid/definition_conversion_skipped_reverse.json` | Permanent invalid-contraction reproducer |
| `tests/fixtures/m1/invalid/duplicate_members.json` | Negative strict-JSON CLI fixture |
| `tests/fixtures/m1/README.md` | Explains negative fixtures and reproducing CLI smoke checks |
| `scripts/run_m1_cli_smoke.py` | Nine production CLI acceptance/rejection checks, including the P0 temporary spec |
| `scripts/verify_m1_frozen_baseline.py` | Recomputes manifest provenance, exact replay identity, and complete M0 non-regression evidence |
| `.github/workflows/m1-trusted-kernel-validation.yml` | Dedicated M1 CI with complete path coverage |
| `audit/m1/FROZEN_SPEC_INTEGRITY_INVENTORY.md` | Explicit specification-consumer inventory and impact trace |
| `audit/m1/FROZEN_M0_NONREGRESSION.json` | Reproducible file and protected-object SHA-256 evidence |
| `audit/m1/M1_TRUSTED_KERNEL_IMPLEMENTATION_LOG.md` | This corrected provenance and repair record |

No repair edit touches `spec/**`, `audit/m0/**`, AGENTS.md, foundational docs,
pyproject.toml, the existing M0 workflow, or any original Python test file.
The six existing positive JSON fixtures are preserved.

## 4. Regression coverage and results

The original audited implementation was run before editing: **958 passed in
4.93s**. Every original test Python file was compared byte-for-byte with
`e083763`; none was removed or modified.

The 108 new integrity cases include independent dropped/renamed/missing field
declarations for atom, neg, poss, and, or, strict_imp, and equiv_s; changed
arity, primitive status, object level, and constructor membership for each;
binary child order; defined-node surface status and removed/unknown/swapped
registered definition links; and conversion-registry LHS association mutations.
There are 65 constructor-declaration cases. Negative cases assert a loader
error before `FrozenBasis`, `deep_freeze`, or `FrozenSpec` construction.

Other new cases preserve the exact invalid contraction and its downstream
uses, the B1 matching counterexample, schema instantiation/metavariables,
occurrence resolution/replacement, atom names, Sa, definition expansion,
diagnostic erasure, seven contract traversal declarations, path/Sb policies,
all six valid kinds on an ordinary copied baseline, raw-byte mutation of each
of six files, snapshot consistency, and rejection of a caller-supplied
manifest. The CLI timing regression forbids certificate reading and theorem
checking when the constructor declaration is altered.

| Executed gate | Result |
| --- | --- |
| `python -m pytest tests/kernel/test_frozen_baseline.py tests/m1/test_ci_coverage.py` using `.venv/bin/python` | **137 passed in 4.54s** |
| `bash scripts/run_m0_checks.sh`: ordinary spec validation | PASS: M0.6, 7 constructors, 12 schemas, 4 Lewis operations, 6 certificate kinds, 5 systems |
| Same script: ordinary source-register validation | PASS |
| Same script: spec freeze validation | PASS |
| Same script: source-register freeze validation | PASS |
| Same script: complete `python -m pytest` suite | **1095 passed in 9.30s**: all 958 retained cases + 137 added cases |
| `python scripts/verify_m1_frozen_baseline.py` using `.venv/bin/python` | PASS: six Git blob identities, 36 protected parsed objects at all five states, pure freeze parent, exact replay tree, all production integrity/semantic checks |
| Compare persisted evidence to pre-edit snapshot | PASS: all 36 object hashes and all six raw file hashes equal |
| `python scripts/run_m1_cli_smoke.py` using `.venv/bin/python` | PASS: six valid fixtures exit 0; invalid contraction and duplicate JSON exit 1; P0-mutated spec exits 2 with `FrozenSpecIntegrityError` |
| Original test files / original M0 workflow preservation | PASS: byte-identical to audited failed M1 |
| `git diff --check` and staged patch whitespace check | PASS |

## 5. Frozen M0 non-regression evidence

Before any repository edit, full parsed protected objects, per-object hashes,
and file hashes were recorded in
`/tmp/lewis-m1-repair-20260908/frozen-before.json`. They were compared across
certified M0, failed M1, and the initial worktree. The deterministic persisted
record is now
[`FROZEN_M0_NONREGRESSION.json`](FROZEN_M0_NONREGRESSION.json), whose 36 object
hashes and six pre-repair file hashes were directly compared to that pre-edit
snapshot. Its verification script recomputes the result from the immutable
Git objects and current files; it does not depend on the temporary record.

The comparison checks all four complete parsed spec documents excluding only
the root administrative status; seven full constructor declarations; all 12
schema ASTs; all three definition LHS/RHS pairs; six normalized basis blocks;
both S5 bridge records as one complete list; the entire canonical certificate
contract; and both complete lock objects. Every protected object is equal at
certified M0, pure freeze, failed M1, replay, and repair. Thus it also covers
primitive-schema metadata, all definition content, and policies beyond the
individually named ASTs through complete-document equality.

From administrative freeze through repair, all six complete input files are
byte-identical, including status and whitespace:

| File | Raw SHA-256 |
| --- | --- |
| `spec/language.yaml` | `716b244cc3b6ca35a5459c0b47c11d8680ebd4f1451d30bb8dc2076fa1aed47e` |
| `spec/rules.yaml` | `35eedb8177ce330f6827b05e9f1d33e30e1a6ec8412a461ea1690c385b9a5e23` |
| `spec/schemas.yaml` | `d7c3fcd5d581f8390345b95cacea9bc8a21a4beaa435919b089c252eab084df3` |
| `spec/systems.yaml` | `84d76ff732dabf24195257fccdb95437392eef21f530a9e852222774b237f2d1` |
| `audit/m0/certified_ast_fingerprints.yaml` | `7e7b124a0abc6bdad238d1393196872b9330fc4637e86b80b1a2ec1f32e85b45` |
| `audit/m0/certificate_contract_lock.yaml` | `5a2885f9665132617d77659c4c497f4b99872e05b2088d6d5ab6bcd556a0e4ba` |

Both lock files are also byte-identical to certified candidate `21117f3`.
The canonical-JSON hash of the entire certificate contract remains
`c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316`.
No forbidden semantic registry, Box, B9, necessitation, object-language equality,
semantic proof step, mixed S5 basis, or implicit definition conversion was added.

## 6. CI coverage and remaining handoff

The dedicated workflow triggers on both push and pull_request for
`src/lewis_prover/**`, `tests/**`, `scripts/**`, `spec/**`, `audit/m0/**`,
`audit/m1/**`, `pyproject.toml`, `AGENTS.md`, and `.github/workflows/**`.
It also permits manual dispatch. The 29 CI regression cases cover nested
production/test/fixture/validation paths for both events and require all
validation commands. Full history is checked out to reproduce the freeze and
replay provenance. The original M0 workflow is unchanged.

The M1 job runs `bash scripts/run_m0_checks.sh`, `python -m pytest`, the frozen
provenance verifier, production CLI smoke checks, `git diff --check`, and
`git diff --check HEAD^ HEAD`. No remote execution result is claimed: this
repair was requested as a local branch without pushing.

All requested local repair gates pass. The remaining handoff is independent
Work Max re-audit of the exact repaired commit; local test success does not
confer M1 certification. No M2 work was performed.

M1 REPAIR COMPLETE — INDEPENDENT RE-AUDIT REQUIRED
