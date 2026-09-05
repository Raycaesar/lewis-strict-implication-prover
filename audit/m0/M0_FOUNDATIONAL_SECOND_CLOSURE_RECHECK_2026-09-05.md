M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED

# Second focused closure recheck of the M0.4 foundational repair

**Repository:** `Raycaesar/lewis-strict-implication-prover`  
**Audited commit:** `5f86547a2f16e5f1e1620823e3b68457fb8350b7`  
**Commit tree:** `1d423cb406abdc982851ec67bcd6d6b6f75f53b8`  
**Parent:** `5339a5a4f4c56a5e4feae3cc452730e488a309f1`  
**Audit date:** 2026-09-05 UTC  
**Mode:** read-only, detached-worktree closure recheck; no M1 code written

## 1. Audit identity and scope

The pasted invocation did not itself contain a new M0.4 SHA. At the start of
the audit, the repository exposed one unambiguous closure candidate: the direct
child of the named M0.3 candidate, with commit subject `close remaining M0
certificate and bridge audit defects`. I therefore detached and pinned the
audit to:

```text
5f86547a2f16e5f1e1620823e3b68457fb8350b7
```

This report applies only to that SHA and tree. The worktree was detached and
clean at the end of inspection. No later state of `main` was used.

The requested primary files were read in the prescribed order. I also checked
the active language, source-policy and architecture files where needed to test
normative consistency. I did not redo the closed historical formula
transcription audit: instead, I compared the locked AST objects directly with
both the previous candidate and the original M0 audit candidate.

## 2. Executive summary

The two former P1 defects are substantively repaired:

1. The exact M0.4 documents now define a closed logical certificate object,
   exact field sets for every justification, nonempty-string identifiers,
   exact string reference identity, duplicate-key rejection, and no trusted
   metadata extension.
2. The S5 bridge records now use operational `from_basis_id` and
   `into_basis_id` fields with the correct orientations and the invariant
   `expanded_certificate.basis_id == into_basis_id`.

The Parry provenance fields, v0.3 `parents` vocabulary, fingerprint metadata,
and candidate-to-frozen status transition are also repaired. All 12 schema
ASTs, all three definition ASTs, and all normalized S1–S5 memberships are
unchanged. The five requested local commands pass, the full suite reports
`30 passed`, no tracked `Zone.Identifier` path exists, and exact-SHA GitHub
Actions is green.

Certification nevertheless fails on one remaining **P2 freeze-integrity
defect**. The new tests mutate newly added policy mirrors and correctly obtain
rejection. But the original, still-active normative fields remain separately
editable. Replaying five of the seven prior semantic counter-mutations against
those original fields still produces:

```text
validate_bundle(..., freeze=True) -> no issues
```

The same problem admits changes to the original node-field and scalar/reference
declarations while their new mirror fields remain unchanged. Nothing in M0.4
declares the ignored fields nonnormative or gives the new mirrors precedence.
Thus `--freeze` can certify an internally contradictory certificate
specification. This is exactly a P2 that undermines freeze integrity, so the
prompt's certification condition (3) is not met.

There is **no remaining P0** and **no remaining P1**. The exact candidate's
current certificate semantics are deterministic; the blocker is the claimed
freeze gate's failure to preserve those semantics under the required
counter-mutations.

## 3. Mandatory question A — P1-01 serialization closure

### 3.1 Exact closed objects

The top-level certificate fields are exactly:

```text
proof_id, system, basis_id, goal, root, nodes
```

Each node has exactly:

```text
conclusion, justification
```

The justification field sets are consistently specified in
`docs/PROOF_CERTIFICATE_SPEC.md` and `spec/rules.yaml`:

| Kind | Exact allowed fields | Parent arity |
| --- | --- | ---: |
| `postulate_instance` | `kind`, `schema_id`, `schema_substitution` | 0 |
| `Sa` | `kind`, `parents`, `atom_substitution` | 1 |
| `Sb` | `kind`, `parents`, `direction`, `occurrence_path` | 2 |
| `Ad` | `kind`, `parents` | 2 |
| `Smp` | `kind`, `parents` | 2 |
| `definition_conversion` | `kind`, `parents`, `definition_id`, `direction`, `occurrence_path` | 1 |

All other fields are rejected at the logical top-level, node, formula-AST and
justification layers. M0.4 provides no certificate metadata field; provenance
or search annotations must remain outside the trusted certificate and cannot
affect validity.

### 3.2 Identifier and reference policy

`proof_id`, node-map keys, `root`, and parent references are nonempty strings.
Reference resolution is exact Unicode codepoint-string identity, without
numeric/string coercion or normalization. The strict YAML loader rejects
duplicate mapping keys before logical checking. The proof DAG additionally
requires resolvable references, acyclicity, root reachability of every node,
parent-before-node acceptance, and exact root/goal structural identity.

### 3.3 Independent-implementation question

**Are two independent M1 implementations now forced to accept the same logical
certificate documents?**

For the exact unmodified documents at the audited SHA: **yes**. The field sets,
types, dispatch, rule payloads, formula identity, basis admission and DAG
conditions are sufficiently closed and mutually consistent to determine the
same logical acceptance set.

For a specification advertised as protected by the present `--freeze` gate:
**no**. The gate can accept a later document containing mutually contradictory
active declarations, as demonstrated in Section 7. That is a validation/freeze
defect, not a remaining ambiguity in the exact candidate and therefore remains
P2 rather than P1.

## 4. Mandatory definition, Sa and occurrence-path checks

### 4.1 Definition conversion

M0.4 uniquely specifies one mechanism for visible use of `DEF_OR`,
`DEF_STRICT_IMP`, and `DEF_EQUIV_S`:

```text
definition_conversion(parent, definition_id, direction, occurrence_path)
```

The node:

- has exactly one parent;
- selects one surface occurrence by the shared path grammar;
- uses direction `expand` or `contract`;
- matches one side of the registered definition with one shared metavariable
  environment;
- requires repeated metavariables to be structurally identical;
- instantiates the opposite side with that same environment;
- changes exactly the selected occurrence; and
- permits no nested or second implicit definition conversion.

Every Lewis primitive-rule match uses the exact visible AST. Full erasure is
diagnostic only. `definition_conversion` is explicitly a trusted
metalinguistic certificate check, not a fifth Lewis inference rule.

There is no circularity with `Sb`: conversion checks only a registered
definition and a structural occurrence; `Sb` neither invokes nor supplies that
conversion. Conversely, `Sb` requires an already accepted first parent whose
surface root is literally `equiv_s`. Any expansion or contraction needed to
obtain that surface form must be a separate checked node.

### 4.2 `postulate_instance` versus `Sa`

The two namespaces and operations are now disjoint:

| Property | `postulate_instance` | `Sa` |
| --- | --- | --- |
| Namespace | explicit schema metavariables such as `{meta: P}` | object atom names |
| Parents | none | exactly one accepted theorem parent |
| Map domain | exactly all metavariables in the registered schema | a nonempty subset of atoms occurring in the parent |
| Application | one simultaneous schema instantiation | simultaneous, one-pass, nonrecursive atom substitution |
| Extra keys | rejected | rejected |
| Rendering | schema label; never cosmetically called `Sa` | an actual `Sa` step |

The parentless/direct schema instance is no longer disguised as Lewis
Substitution (b).

### 4.3 Shared occurrence paths

`Sb` and `definition_conversion` use the same normative list grammar:

```text
root = []
segments = arg | left | right
```

`neg` and `poss` expose only `arg`; `and`, `or`, `strict_imp`, and `equiv_s`
expose only `left` and `right`; `atom` exposes no formula child.
`atom.name`, integer indices, dotted strings, unknown segments and paths leaving
the tree are invalid. Defined nodes are traversed as surface nodes, without
expansion. Each node changes exactly one selected occurrence.

These provisions close the former P1 occurrence-path and definition-conversion
questions in the exact candidate.

## 5. Mandatory question B — P1-02 S5 bridge direction

The operational meanings are now unambiguous:

- `from_basis_id`: basis of the compact/source proof being translated;
- `into_basis_id`: basis in which the expanded native certificate is checked.

The mandatory invariant is repeated consistently:

```text
expanded_certificate.basis_id == into_basis_id
```

The stored obligations have the required orientations:

| Translation | `from_basis_id` | `into_basis_id` | Primitive recovered in the `into` basis | Stored expansion basis |
| --- | --- | --- | --- | --- |
| primary → alternative | `S5_PRIMARY_B1_B7_C11` | `S5_ALT_B1_B7_C10_C12` | `C11` | alternative |
| alternative → primary | `S5_ALT_B1_B7_C10_C12` | `S5_PRIMARY_B1_B7_C11` | `C10`, `C12` | primary |

Thus no characteristic axiom can satisfy its bridge merely by being checked in
the basis where it is already primitive. Primary S5 admits C11 but not C10/C12;
alternative S5 admits C10/C12 but not C11; the union is forbidden; and every
proof declares one allowed `(system, basis_id)` pair.

The former bridge P1 is closed without changing either S5 basis.

## 6. Mandatory questions C, E and F — provenance, documentation and non-regression

### 6.1 Parry and L&L provenance

All seven active Parry S3 fields named by the prior recheck now contain the
reduced list:

```text
11.1-11.4, 11.6, 11.7, 30.1/A8
```

and state that 11.5 is supplied by the McKinsey derivation discussed on p. 138.
The validator enumerates those seven fields, and the old full-list shorthand
survives only in historical audit material or negative tests.

All three active p. 498 bridge-source entries retain the paragraph's explicit
`A1-A8/B1-B9` background and say that the historical statement is not itself a
native B1–B7 bridge certificate. Each identifies L&L p. 501 as the canonical
direct source for the B1–B7-based S5 presentations.

### 6.2 Repair-log vocabulary and state transition

The superseded v0.3 repair log now records the normative one-element payload:

```yaml
parents: [<node-id>]
```

rather than singular `parent`.

The source validator accepts `repair_implemented_reaudit_pending` for a
closure candidate and requires `closed` once the register is
`frozen_source_audit`. The supplied transition test passes. Independently
changing all four executable-spec statuses together from `candidate_m0` to
`frozen_m0` also passes both normal and freeze validation. The transition is
therefore not blocked by the validator.

### 6.3 Fingerprint lock

Freeze validation checks:

```text
lock_version = 0.2
formula_source_audit_commit = 4931e4daa124587a789ac27b841f499295facf5e
formula_nonregression_recheck_commit = 5339a5a4f4c56a5e4feae3cc452730e488a309f1
```

It also checks coverage and hashes for all 12 schema ASTs and all three
metadefinition ASTs. A metadata mutation is rejected. The lock correctly and
explicitly warns that a deliberate simultaneous AST-and-hash edit cannot be
authenticated automatically and requires a new human/Work Max foundational
audit. That limitation is acceptable because it is accurately documented.

The fingerprint lock does not protect certificate-rule prose, source
provenance, display strings or system membership; the latter categories need
their own checks. This limitation is material to the remaining P2 in Section
7.

### 6.4 Object-level non-regression

Direct canonical-object comparison produced:

| Locked layer | Compared with `5339a5a…` | Compared with `4931e4da…` | Result |
| --- | --- | --- | --- |
| B1–B8, A8, C10–C12 ASTs | all 12 equal | all 12 equal | unchanged |
| `DEF_OR`, `DEF_STRICT_IMP`, `DEF_EQUIV_S` LHS/RHS ASTs | all 3 equal | all 3 equal | unchanged |

Normalized membership is also unchanged:

| Basis ID | Resolved schemas |
| --- | --- |
| `S1_B1_B7` | B1–B7 |
| `S2_B1_B8` | B1–B8 |
| `S3_B1_B7_A8` | B1–B7, A8 |
| `S4_B1_B7_C10` | B1–B7, C10 |
| `S5_PRIMARY_B1_B7_C11` | B1–B7, C11 |
| `S5_ALT_B1_B7_C10_C12` | B1–B7, C10, C12 |

The M0.4 repair is therefore certificate/provenance/validation-only in logical
effect. No source or formula re-audit was triggered.

## 7. Mandatory question D — validator, mutations and exact-SHA CI

### 7.1 Requested commands

All requested checks were run in the detached worktree:

| Command | Result |
| --- | --- |
| `python scripts/validate_spec.py` | PASS |
| `python scripts/validate_source_register.py` | PASS |
| `python scripts/validate_spec.py --freeze` | PASS |
| `python scripts/validate_source_register.py --freeze` | PASS |
| `python -m pytest` | PASS — 30 tests in 0.71 s |
| `git ls-files '*:Zone.Identifier'` | no output |

The initial environment did not have the `pytest` executable installed. After
installing the repository's declared `.[dev]` extras, the suite ran under
Python 3.12.13 and pytest 8.4.2. The repository worktree remained clean.

Exact-SHA GitHub Actions also passed: [M0 spec validation run
33908037532](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/33908037532)
completed successfully for head SHA `5f86547a…`. The single
`validate-m0-spec` job and every step—including Zone rejection, both normal
validators, both freeze validators and pytest—reported `success`.

These results establish reproducibility of the encoded checks. They do not by
themselves establish that the checks cover every active normative declaration.

### 7.2 Repository-supplied rejection tests

The focused repository tests pass for:

- the seven newly encoded mutation cases;
- bridge orientation and expansion basis;
- global and justification-level unknown-field policy;
- integer/string parent-reference policy;
- Parry provenance;
- fingerprint metadata; and
- candidate-to-closed/frozen status transition.

A focused run of the seven counter-mutation tests plus the four additional
requested rejection tests reported `11 passed`. Independent direct mutations
of `reference_resolution`, the bridge's
`expanded_certificate_basis_id`, and a justification's `allowed_fields` were
also rejected with `ID_EQUALITY`, `BRIDGE_DIRECTION`, and
`KIND_ALLOWED_FIELDS`, respectively.

### 7.3 Exact replay against the original active fields

The repository tests do not mutate the same original semantic fields that made
the prior freeze gate produce false positives. M0.4 adds new machine-readable
mirror fields and mutates those instead. Replaying the prior semantic changes
against the original fields gives:

| Counter-mutation applied to an active original field | Freeze result | Why the new test misses it |
| --- | --- | --- |
| Weaken `kernel_certificate_kinds.postulate_instance.schema_substitution.domain` to permit missing keys | **ACCEPTED** | validator checks only new `domain_policy` / key-policy mirrors |
| Replace `definition_conversion.check`'s one shared environment instruction with independent environments | **ACCEPTED** | validator checks only new `metavariable_environment_policy` |
| Replace `definition_conversion.check`'s no-second-conversion instruction with permission for further implicit conversions | **ACCEPTED** | validator checks only new `implicit_additional_conversion` |
| Change `primitive_rules.Sb.constraints` to allow multiple occurrence replacements | **ACCEPTED** | validator checks only new `replacement_count` |
| Change `occurrence_path_grammar.traversal` to make `atom.name` traversable | **ACCEPTED** | validator checks only new `atom_traversable_fields` |
| Swap the actual S5 `from_basis_id` / `into_basis_id` orientation | rejected (`BRIDGE_DIRECTION`) | operational records are directly checked |
| Change the actual unknown-justification-field policy to ignore | rejected (`JUSTIFICATION_UNKNOWN`) | active policy is directly checked |

Thus only two of the seven semantic replays are actually closed at every active
representation. Five still pass `validate_bundle(..., freeze=True)` with zero
issues.

The same duplication problem affects the newly repaired serialization layer:

| Additional active-field mutation | Freeze result |
| --- | --- |
| Add `metadata` to `proof_node_grammar.node_fields` | **ACCEPTED** |
| Set `proof_node_grammar.no_extra_node_fields` to false | **ACCEPTED** |
| Change `certificate_serialization.scalar_types.node_reference` to `string_or_integer` | **ACCEPTED** |
| Change `certificate_serialization.string_identity` to coercive identity | **ACCEPTED** |

The parallel `allowed_node_fields`, `unknown_node_fields_policy`,
`node_id_policy`, and `reference_resolution` mirrors remain unchanged in these
mutations, so the validator sees the expected constants and returns PASS even
though the executable source now contradicts itself.

This is not a complaint that M0 lacks an M1 certificate checker. A structural
M0 validator can and should reject contradictory foundational declarations.
The defect is specifically that the gate protects only one copy of duplicated
normative content while `spec/rules.yaml` and the architecture give no rule
making the other copy nonnormative.

## 8. Full P0–P3 defect register

### P0

**None.** Definition conversion remains uniquely specified and noncircular.

### P1

**None.** P1-01 closed serialization and P1-02 operational bridge direction
are both closed in the exact candidate.

### P2-01 — the freeze gate still admits the prior semantic mutations through duplicate active fields

1. **Exact locations:**
   - active declarations in `spec/rules.yaml:17–49, 64–99, 183–211,
     247–284, 320–389, 397–434`;
   - partial checks in `scripts/validate_spec.py:295–409`;
   - mirror-only mutations in
     `tests/spec/test_second_closure_mutations.py:16–69` and
     `tests/spec/test_closed_serialization.py:16–57`;
   - overclaim in `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.4.md:105–124`.
2. **Exact defect:** M0.4 duplicates foundational semantics in old prose/data
   fields and new policy/registry fields. Freeze validation generally checks
   only the new copy. It accepts changes to the old `domain`, `check`,
   `constraints`, `traversal`, `node_fields`, `no_extra_node_fields`,
   `scalar_types`, and `string_identity` declarations while the mirror remains
   unchanged. No normative-precedence rule declares those old fields
   commentary or generated text.
3. **Why it matters:** `--freeze` can return PASS for an internally
   contradictory trusted-certificate specification. Two implementers reading
   different active declarations could then accept different certificate sets,
   even though both relied on a commit advertised as freeze-valid. This is the
   unresolved P2 specifically prohibited by certification condition (3).
4. **Required repair:** establish one authoritative representation. Either
   remove/generate/explicitly mark the duplicate prose fields as nonnormative,
   or validate every duplicate against the same canonical contract. Add
   rejection tests that mutate each original field independently, including
   all five accepted replays and the four serialization mutations above. A
   canonical hash/manifest for the certificate contract is also acceptable if
   its update policy requires focused re-audit.
5. **Changes intended calculus?** No. The repair should preserve every current
   certificate rule, formula AST, definition AST and basis membership.
6. **Re-audit dependency:** certificate-contract structure, validator and
   mutation tests only. Re-run all five requested commands, the nine accepted
   mutations above, Zone rejection and exact-SHA CI. No formula-by-formula or
   historical-source re-audit is needed unless a locked logical object changes.

### P3

**None required for closure.** Optional additional hardening must not distract
from P2-01.

## 9. Exact freeze-checklist status

| Freeze item | Observed status at audited SHA |
| --- | --- |
| Worktree pinned to exact commit | PASS — detached, clean |
| Four requested validators | PASS |
| Full pytest suite | PASS — 30/30 |
| Tracked Zone metadata absent | PASS |
| Exact-SHA GitHub Actions | PASS — run 33908037532 |
| P0 absent | PASS |
| P1 absent | PASS |
| Parry/p.498/p.501 provenance closure | PASS |
| Locked AST and basis non-regression | PASS |
| Post-certification status transition supported | PASS |
| Seven prior semantic counter-mutations all rejected | **FAIL — 5/7 accepted through original active fields** |
| No freeze-undermining P2 | **FAIL — P2-01 remains** |
| Independent closure certification | **FAIL** |

The cleanup script was not executed because this was expressly a read-only
audit and it performs deletions. Its intended result was checked safely instead:
the exact commit tracks no `Zone.Identifier` file, and both local and CI hygiene
checks pass.

## 10. Minimal repair plan

1. Designate one canonical machine-readable certificate contract in
   `spec/rules.yaml`.
2. Remove, generate, or explicitly demote every redundant semantic copy; if
   copies remain normative, validate their exact agreement.
3. Add negative tests for all five accepted original-field replays and the four
   accepted serialization-field mutations.
4. Correct the v0.4 repair log's claim that all seven demonstrated mutations
   are already structurally rejected.
5. Run the five required local commands, Zone check and exact-SHA CI on the new
   immutable candidate.
6. Perform one narrow P2 closure recheck. Preserve the existing fingerprints
   and resolved bases; a formula/source re-audit remains unnecessary unless
   those locks change.

## 11. Final recommendation

The M0.4 repair closes both former P1 defects and leaves the intended calculus
intact. It does not yet close the advertised freeze gate against the exact
semantic mutations that motivated the repair. Under the supplied certification
standard, the audited commit cannot be frozen as M0.

**M1 trusted-kernel implementation may not begin yet.** Complete P2-01 and run
one narrowly scoped validator/mutation closure recheck; no mathematical
replacement of the schema, definition or S1–S5 system layer is indicated.
