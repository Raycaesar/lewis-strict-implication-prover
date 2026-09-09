# M1 Trusted Kernel Implementation and Audit Repair Log

First repair verification: 2026-09-09 (Asia/Shanghai; 2026-09-08 UTC).
Second repair verification: 2026-09-09 (Asia/Shanghai).
Repository: `Raycaesar/lewis-strict-implication-prover`.

The independent Work Max closure audit of first repair candidate
`b5d543db60ed7631f9e182f137ce2f83156d2ec3` returned
**M1 TRUSTED KERNEL NOT CERTIFIED**. The file-loader P0 and both P2 findings
were closed, but one P0 remained: public Python checking accepted unvalidated
specification objects. Sections 1–6 retain the first-repair history, with its
scope corrected; section 7 records the present Python API repair. Local test
success does not confer M1 certification. M2 and proof search remain unimplemented.

## 1. Exact provenance and reconstructed history

| Identity | SHA / value |
| --- | --- |
| Certified M0 candidate | `21117f3da827f873c3ed88b578a1681aabfca7ac` |
| Historical report-only commit / unchanged tag `m0-foundational-spec-v1` | `3ded752aef28be17509649fbcd47a3daf29c7279` |
| Pure administrative M0 freeze, reconstructed locally | `33e6a14a4b92534ea159868060576d1b45da9bb5` |
| M1 implementation baseline, exact tree replay on that freeze | `d87f1145da766f4ccbb7a9f9b76e9d15328d50da` |
| Audited failed M1 SHA | `e0837632aa9e187ccbc5a6fcc1a3a8816e17fe56` |
| Failed first closure candidate | `b5d543db60ed7631f9e182f137ce2f83156d2ec3` |
| Second repair candidate, direct child of b5d543 | `PENDING_FINAL_COMMIT` |
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
      -> b5d543  first M1 repair (file-loader P0 and both P2 findings closed)
        -> PENDING_FINAL_COMMIT  second M1 repair (Python API boundary)
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

### Complete file-loader input boundary

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
links but is outside certificate acceptance. The first repair authenticated
these fields only on the file-loader path. It did not enforce that invariant
on directly supplied Python models; the earlier claim of complete input-path
protection was incorrect. Section 7 records the production API enforcement.
No transform semantics were changed by either repair.

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

All first-repair local gates passed, but the subsequent independent closure
audit found the Python API P0 described below. The earlier local completion
statement was not certification or evidence that the complete API boundary
was protected.

## 7. Second repair: M1-CLOSE-01 Python specification trust boundary

### Audit input, exact root cause, and reproduction

Failed first closure candidate: `b5d543db60ed7631f9e182f137ce2f83156d2ec3`.
The supplied independent report is preserved in
[`M1_CLOSURE_REPORT_b5d543_FINAL.md`](M1_CLOSURE_REPORT_b5d543_FINAL.md).
It was an untracked audit input at the start of this task and is included as
evidence with this repair. Staging exposed two trailing-space Markdown hard
breaks; they were converted to equivalent backslash hard breaks to satisfy
`git diff --check`. All other bytes are unchanged. The original byte-for-byte
copy is `/tmp/lewis-m1-second-repair-closure-report-original.md`, whose SHA-256
matches the pre-edit snapshot. Its statements and links concern the previous
candidate and its audit environment, not certification of the new candidate.

The exact remaining root cause was an unenforced loader-origin precondition.
Public `FrozenSpec` and `FrozenBasis` constructors are ordinary data builders;
frozen dataclasses do not authenticate their fields, and their nested values
can remain caller-owned and mutable. `check_certificate` passed the supplied
spec through unchanged, `NodeChecker.__init__` retained it, and trusted
transforms and `validate_basis` read its unchecked constructor/definition/
contract/basis data. Complete file hashes protected only callers that entered
through `load_frozen_spec`.

Before changing production code, five new cases failed against b5d543:
the existing three-node skipped-reverse contraction fixture, a two-node B5
variant with contraction at its left occurrence, incremental construction
with the altered spec, B8 admission under S1 through an invented `FrozenBasis`,
and an existing incremental session whose semantics changed through a retained
nested dictionary alias. Both serialized conversion variants and the B8
certificate were falsely accepted; the retained-alias conversion was also
accepted. Genuine M0 rejected the same invalid conversion/admission claims.
These tests changed only caller data and did not patch the production loader,
manifest, private acceptance ledger, or interpreter state.

### One authoritative validation boundary

`kernel.frozen_spec.validate_frozen_spec` now establishes the invariant for
every supported specification-dependent API and returns the checker-owned
immutable M0 authority. That authority is initialized only after the existing
loader has authenticated all six original file blobs and passed every
metadata, AST fingerprint, contract-lock, and normalized-basis check. It is a
snapshot of the existing YAML authority, not an independently editable
semantics registry. No baseline digest or M0 semantic declaration changed.

The comparison includes complete `language`, `rules`, `schemas`, and `systems`
documents; `spec_version`; the separately exposed canonical contract; and the
complete derived basis table. This covers all seven constructor declarations,
12 primitive ASTs, three definition pairs and links, the entire contract and
occurrence/traversal declarations, all normalized bases and S5 separation,
and every derived basis's `system_id`, `basis_id`, `schemas`, `rules`, and
`alternative` field. Missing/extra mapping members and changed sequence order
reject. Scalar types must agree exactly; Python's `True == 1` coercion and
caller-defined equality cannot impersonate a declaration. Equivalent ordinary
list/tuple and set/frozenset representations are permitted.

Only `repository_root` is nonsemantic location metadata. If direct model
construction is the first API call in a process, that root locates the files
for the ordinary authenticated loader; it never supplies a trusted manifest.
After initialization, comparisons use the in-memory authenticated authority.
Every later explicit `load_frozen_spec` call still rereads and authenticates
all six files before returning a result. Cached semantics never bypass file
integrity checks, including when loading a previously valid directory again.

There is no validated flag, provenance token, digest field, or transferable
validation marker. Reconstructed and copied objects receive content checks.
Identity shortcuts apply only to actual immutable values in the authenticated
reference graph. The validator returns that graph and never caches or retains
a caller's mutable representation as trusted. An altered specification raises
`FrozenSpecIntegrityError` before certificate/transform acceptance work.

### Protected production entry points and immutability

The before/after input inventory was written before implementation and is in
[`FROZEN_SPEC_INTEGRITY_INVENTORY.md`](FROZEN_SPEC_INTEGRITY_INVENTORY.md).
Enforcement is present in `check_certificate`, `load_certificate`,
`certificate_from_document`, `NodeChecker.__init__`, every `check_node` call,
`validate_basis`, `schema_metavariables`, `instantiate_schema`, `match_schema`,
`object_atom_names`, `substitute_atoms`, `resolve_occurrence`,
`replace_occurrence`, and `convert_definition`. The public diagnostic-only
`diagnostic_full_erasure` also validates its spec for consistent behavior; it
remains outside theorem acceptance. `validate_frozen_spec` is exported at both
the kernel and package surfaces.

Every entry uses the validator's returned snapshot, and incremental sessions
store only that snapshot. Private underscore transform helpers are explicitly
internal and receive their patterns/environments only through these validated
operations. No supported trusted API accepts a standalone `FrozenBasis`, a
caller-prepared constructor registry, or external transform matching state.

The authority's mappings are `MappingProxyType` over freshly copied
dictionaries; YAML sequences become tuples. Derived bases are frozen
dataclasses containing immutable strings, frozensets of schema names, tuples
of rule names, and booleans. There are no mutable descendants. A caller's
shallow proxy can retain mutable descendants, but none become checker state.
Accepted equivalent mutable data is discarded after comparison in favor of
the authority snapshot. Later alias mutation cannot change an existing
session, returned basis, or trusted transform; reusing the changed original
spec for another operation rejects.

### Regression results and preserved behavior

`tests/kernel/test_python_api_boundary.py` adds **299 cases**: every supported
spec-using API against every top-level semantic component; all constructor
declarations, ASTs and definition links; every derived basis field; invented
and mixed bases; all required primitive admission probes; copied and rebuilt
models; fake markers; nested aliases and mutable basis members/rules; recursive
immutability; exact scalar types and dishonest equality; and first API calls
in fresh interpreters. Positive controls exercise every API with loader data
and equivalent mutable reconstructions, all six justification fixtures as
complete DAGs and incremental sessions, and all three definitions in both
directions at root and nested occurrences.

`tests/kernel/test_file_integrity_closure.py` adds **69 cases** repeating the
mutation classes published in the independent closure report. Each begins
with a valid loaded temporary copy and then mutates it, so the tests also
verify that an initialized authority cannot bypass later file checks. These
are permanent reproductions of the published classes; the independent audit's
temporary scripts are not required or claimed as reused artifacts. All 69
reject. All existing 108 first-repair file-integrity tests are retained.

| Exact probe | Second-repair result |
| --- | --- |
| Existing skipped-reverse fixture and two-node B5 variant, genuine spec, whole checker | Reject: `invalid_definition_conversion`, node `root`, detail `DEFINITION_CONVERSION` |
| Same conversion through a caller-constructed spec with `and.fields = [left]` | Reject: `FrozenSpecIntegrityError` before logical checking |
| Incremental construction with that altered spec | Reject: `FrozenSpecIntegrityError` |
| Incremental session followed by retained-alias constructor mutation | Reject invalid conversion with `DEFINITION_CONVERSION`; no invalid ledger entry |
| Direct inconsistent B1 matching / skipped-reverse conversion, genuine spec | Reject: `SchemaMatchError` / `DefinitionConversionError` |
| Those direct transforms with an altered spec | Reject: `FrozenSpecIntegrityError` |
| B8 under S1, genuine or semantically identical reconstructed spec | Whole and incremental rejection: `SCHEMA_ADMISSION` |
| B8 under S1 via forged derived basis or changed mutable basis alias | Forged spec rejects with `FrozenSpecIntegrityError`; existing session still rejects with `SCHEMA_ADMISSION` |
| A8 under S2; C11 under S5 alternative; C10/C12 under S5 primary | Reject: `SCHEMA_ADMISSION` |
| B8 under S2; A8 under S3; C10 under S4; C11 under S5 primary; C10/C12 under S5 alternative | Accept exact primitive instance |
| Genuine loader spec, all existing valid fixtures, complete DAGs and six kinds | Accept |
| DEF_OR / DEF_STRICT_IMP / DEF_EQUIV_S, expand and contract, root and nested | Preserve exact frozen surface results |

### Full verification and M0 preservation

| Gate | Result |
| --- | --- |
| Pre-edit `bash scripts/run_m0_checks.sh` | Four M0 gates pass; **1,095 passed in 9.84s** |
| Pre-edit frozen baseline/provenance verifier | PASS: six blobs, 36 protected objects, pure freeze, exact replay |
| Five new P0 regression cases before production repair | All five fail as expected; false acceptance reproduced |
| Direct Python API regression suite after repair | **299 passed in 0.64s** |
| Published file-loader mutation matrix | **69 passed in 4.51s**; all mutations reject |
| Post-repair `bash scripts/run_m0_checks.sh` | All four M0 validation gates pass; complete pytest suite **1,463 passed in 15.17s**, no failures/errors/skips |
| `scripts/verify_m1_frozen_baseline.py` | PASS; persisted evidence remains exact |
| `scripts/run_m1_cli_smoke.py` | All nine pass: six valid kinds exit 0, invalid conversion and duplicate JSON exit 1, altered file spec exits 2 |
| Before/after raw-hash comparison | PASS: all eight frozen-file/manifest/evidence hashes unchanged; original closure report's hash preserved in `/tmp`; committed report differs only by two equivalent Markdown hard-break spellings |
| Comparison against b5d543 | PASS: all 83 pre-existing files under frozen/admin authorities, original tests/fixtures, foundational docs, and CI scopes remain byte-identical |
| `git diff --check` and staged `git diff --cached --check` | PASS after normalizing the supplied report's two Markdown hard breaks |

All 1,095 previous tests remain, with **368 new permanent cases**. The
pre-edit snapshot is `/tmp/lewis-m1-second-repair-before.json`; its raw hashes
were compared after repair. The unchanged committed
`FROZEN_M0_NONREGRESSION.json` and verifier independently reproduce all six
input hashes and 36 protected-object comparisons. All seven constructor
declarations, 12 schema ASTs, three definition AST pairs, six normalized basis
blocks, both S5 identities, bridge records, the entire contract, both locks,
and the frozen manifest digests are unchanged. The contract digest remains
`c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316`.

### Files changed, CI, and candidate handoff

Relative to b5d543, production changes are confined to:
`src/lewis_prover/kernel/{frozen_spec,model,basis,certificate,checker,dag,transforms,__init__}.py`,
`src/lewis_prover/{__init__,errors}.py`, and `src/lewis_prover/syntax/erasure.py`.
They add spec authentication, snapshot use, and corrected API documentation;
no logical operation was altered. The two new test files above, this log,
the updated integrity inventory, and the supplied closure report (two Markdown
hard-break spellings normalized)
are the remaining changed/added files.

Both existing workflows and all 29 CI-coverage cases remain unchanged. The
new files fall within existing `src/lewis_prover/**`, `tests/**`, and
`audit/m1/**` push/PR filters and are automatically included in complete
pytest execution. All locally executable CI gates passed. Hosted CI for the
new SHA has not been run; no push or remote branch update was requested or
performed in this second repair. The previous candidate's successful hosted
runs, recorded in the closure report, are not results for the new candidate.

The second repair is one new commit directly on b5d543. The certified M0,
administrative freeze, exact M1 replay and first-repair commits are preserved;
no history was reconstructed, squashed, amended or rewritten in this task.
Final candidate: `PENDING_FINAL_COMMIT` (self-hash cannot be embedded in this
commit; exact SHA is recorded in final delivery). Independent re-audit remains
required. No remaining local test failure is known. No M2 work, proof search,
or M1 certification claim is included.

M1 SECOND REPAIR COMPLETE — INDEPENDENT RE-AUDIT REQUIRED
