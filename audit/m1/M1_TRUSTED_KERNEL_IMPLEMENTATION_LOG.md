# M1 Trusted Kernel Implementation Log

Verification date: 2026-09-08 (UTC). Repository: `Raycaesar/lewis-strict-implication-prover`.
This is an implementation review and local verification record, not certification.

## 1. Baseline, candidate identity, and release gate

| Identity | Observed value |
| --- | --- |
| Independently certified M0 logical anchor | `21117f3da827f873c3ed88b578a1681aabfca7ac` |
| Existing intended freeze tag | `m0-foundational-spec-v1` |
| Commit resolved by that tag and current HEAD | `3ded752aef28be17509649fbcd47a3daf29c7279` |
| Actual committed administrative frozen-status baseline | **NOT AVAILABLE — required provenance gate failed** |
| Final M1 candidate commit | `PENDING_FINAL_COMMIT` |

**Finding M1-GATE-01:** the commit named “freeze certified M0 foundational
specification” adds only
`audit/m0/M0_FOUNDATIONAL_M0_6_DUPLICATE_KEY_CLOSURE_RECHECK_2026-09-05.md`.
At that exact commit all four executable spec statuses remain `candidate_m0`.
The source register and four dependent obligations likewise retain their
pre-freeze statuses. The administrative transitions exist only in the current
uncommitted worktree.

The certification report explicitly conditions the start of M1 on an
administrative frozen-status commit (report lines 20 and 249–258). A tag name
or a green worktree test run does not establish that this condition was met.
There is no M1 commit in the current branch history either.

Local implementation tests are green and no changed frozen logical object was
found. Nevertheless, this log cannot identify the required committed frozen
baseline or certify the historical ordering of uncommitted changes. The final
readiness marker is therefore **NOT COMPLETE**, not the audit-ready marker.

No commit, tag movement, history rewrite, push, or external audit submission
was performed. Resolve and document the missing administrative baseline and
ordering deviation, then rerun this verification before submitting an exact
M1 candidate SHA to Work Max. Do not silently combine the pending M0
administrative transition and M1 implementation and call the result an
already-established frozen baseline.

## 2. Frozen M0 immutability comparison

Read again in this review:

- `AGENTS.md` and `docs/FOUNDATIONAL_SPEC_v0.6.md`;
- all four `spec/*.yaml` authorities, including every field of
  `rules.yaml#canonical_certificate_contract`;
- `audit/m0/certified_ast_fingerprints.yaml` and
  `audit/m0/certificate_contract_lock.yaml`;
- `docs/PROOF_CERTIFICATE_SPEC.md` as nonnormative rendering;
- the 43 entries in `audit/m0/foundational_obligations.yaml`;
- the certification report, repository validation script, and CI workflow.

Git comparison was made against both the certified anchor and the existing
intended freeze tag. Parsed YAML comparison found exactly:

| File | Changes relative to the tagged commit |
| --- | --- |
| `spec/language.yaml` | `status: candidate_m0 -> frozen_m0` only |
| `spec/rules.yaml` | `status: candidate_m0 -> frozen_m0` only |
| `spec/schemas.yaml` | `status: candidate_m0 -> frozen_m0` only |
| `spec/systems.yaml` | `status: candidate_m0 -> frozen_m0` only |
| `audit/m0/source_register.yaml` | Root `status -> frozen_source_audit`; `certificate_contract.status -> closed` |
| `audit/m0/foundational_obligations.yaml` | Only M0-C05, M0-C06, M0-V04, M0-FP04 status/closure evidence; `candidate_state` and `summary.closure_note` freeze accounting |
| `audit/m0/FREEZE_CHECKLIST.md` | Administrative status/checklist prose |
| `docs/FOUNDATIONAL_SPEC_v0.6.md` | Status line and M1-gate prose only |
| `docs/ARCHITECTURE.md` | Current-status heading only |
| `docs/ROADMAP.md` | Current status, completed audit checkboxes, and freeze-summary prose |

All four spec objects are identical to each compared commit after removing
only their root `status` fields. Thus every formula/schema/definition AST,
normalized basis, both S5 bridge records, and the entire canonical certificate
contract are unchanged. Other files in `spec/**`, `audit/m0/**`, and the frozen
foundational document archive have no Git differences. These are the
administrative changes authorized by Prompt 00, already present on entry to
Prompt 09; this review did not write any protected M0 file. They are not
silently represented here as committed M1 changes or as a clean baseline.

Both lock files are byte-identical to the certified anchor and tagged commit:

| Object | SHA-256 |
| --- | --- |
| Raw `certified_ast_fingerprints.yaml` bytes | `7e7b124a0abc6bdad238d1393196872b9330fc4637e86b80b1a2ec1f32e85b45` |
| Raw `certificate_contract_lock.yaml` bytes | `5a2885f9665132617d77659c4c497f4b99872e05b2088d6d5ab6bcd556a0e4ba` |
| Canonical JSON of the complete certificate contract | `c43e0ba61a2f2429c1a7f6f78c3c2e139b7ad4205ec99fadabc7a29766780316` |

The lock's own `candidate_m0_contract_lock` status is intentionally unchanged:
Prompt 00 did not authorize editing that pinned object.

## 3. Exact added/changed file inventory

The following 39 M1 files are new relative to the tagged commit, and were
already present when Prompt 09 began:

```text
src/lewis_prover/__init__.py
src/lewis_prover/__main__.py
src/lewis_prover/cli.py
src/lewis_prover/errors.py
src/lewis_prover/kernel/__init__.py
src/lewis_prover/kernel/basis.py
src/lewis_prover/kernel/certificate.py
src/lewis_prover/kernel/certificate_model.py
src/lewis_prover/kernel/checker.py
src/lewis_prover/kernel/dag.py
src/lewis_prover/kernel/document.py
src/lewis_prover/kernel/frozen_spec.py
src/lewis_prover/kernel/model.py
src/lewis_prover/kernel/transforms.py
src/lewis_prover/render.py
src/lewis_prover/syntax/__init__.py
src/lewis_prover/syntax/erasure.py
src/lewis_prover/syntax/formula.py
src/lewis_prover/syntax/parser.py
src/lewis_prover/syntax/pretty.py
tests/fixtures/m1/Ad.json
tests/fixtures/m1/README.md
tests/fixtures/m1/Sa.json
tests/fixtures/m1/Sb.json
tests/fixtures/m1/Smp.json
tests/fixtures/m1/definition_conversion.json
tests/fixtures/m1/postulate_instance.json
tests/kernel/test_basis.py
tests/kernel/test_certificate_document.py
tests/kernel/test_certificate_structure.py
tests/kernel/test_checker_a.py
tests/kernel/test_checker_b.py
tests/kernel/test_dag.py
tests/kernel/test_frozen_spec.py
tests/kernel/test_transforms.py
tests/m1/conftest.py
tests/m1/test_adversarial.py
tests/m1/test_cli.py
tests/syntax/test_formula.py
```

M1 changes the existing `pyproject.toml` only to discover packages under `src`
and add `src` to pytest's Python path. Runtime dependencies remain PyYAML and
the standard library; pytest is a development dependency.

Prompt 09 adds only this tracked-candidate document:

```text
audit/m1/M1_TRUSTED_KERNEL_IMPLEMENTATION_LOG.md
```

The other 13 modified tracked files are the pre-existing administrative
transition, not M1 logical edits:

```text
AGENTS.md
PACKAGE_MANIFEST.txt
README.md
audit/m0/FREEZE_CHECKLIST.md
audit/m0/foundational_obligations.yaml
audit/m0/source_register.yaml
docs/ARCHITECTURE.md
docs/FOUNDATIONAL_SPEC_v0.6.md
docs/ROADMAP.md
spec/language.yaml
spec/rules.yaml
spec/schemas.yaml
spec/systems.yaml
```

`PACKAGE_MANIFEST.txt` only adds the certification-report pathname. The report
itself is already in the tagged commit. Existing M0 tests, scripts, and CI
workflow were not edited. Virtual-environment installation, ignored coverage
data, build metadata, and temporary negative fixtures are not candidate source
files. The worktree remains intentionally uncommitted; a plain `git diff`
alone does not inventory the untracked M1 files.

## 4. Architecture and trusted entry points

```text
frozen YAML + pinned locks -> load_frozen_spec -> immutable FrozenSpec
canonical bytes/text -> strict document decoder -> closed structural models
                     -> complete DAG + six node checks -> CheckedCertificate
CheckedCertificate -> untrusted renderer -> text / display line numbers
```

`check_certificate(data, frozen_spec)` is the whole-certificate acceptance API.
It takes bytes, bytearray, or text, not a Python mapping, a prebuilt
`ProofCertificate`, or a claimed `CheckedCertificate`. The supplied spec must
come from `load_frozen_spec`. The CLI authenticates the spec itself first.

`load_certificate` and `certificate_from_document` produce structural data,
not proof acceptance. The latter cannot recover duplicates already discarded
by another parser and explicitly says so. `NodeChecker` checks individual
nodes in a private, basis-specific accepted-parent ledger; it is not a
replacement for the whole-DAG API. No ledger-import or theorem-cache interface
seeds accepted nodes.

Frozen dataclasses, mapping proxies, tuples, and frozensets expose read-only
results. Schema and definition patterns are read from the frozen registry,
not re-authored as Python theorem constants.

## 5. Canonical document decoder: field-by-field review

Authority: `canonical_certificate_contract.document_boundary`.
Implementation: `kernel/document.py`; strict orchestration in
`kernel/certificate.py` and `kernel/dag.py`.

| Frozen field | Implementation and reviewed behavior |
| --- | --- |
| `canonical_serialized_format` | Only `utf8_json_rfc8259_object`; no YAML certificate path |
| `accepted_serialized_formats_at_kernel_boundary` | The single JSON format; unsupported Python input types reject |
| `alternative_frontend_formats` | No alternative import frontend implemented |
| `text_decoding` | Byte input uses explicit UTF-8 `errors="strict"` |
| `top_level_document_type` | Pair-preserving decoded value must be a JSON object |
| `duplicate_mapping_keys_policy` | Reject names before object mappings are materialized |
| `duplicate_key_scope` | Recursive check of every object, including objects inside arrays |
| `duplicate_key_identity` | Decoded string code-point identity; no normalization, folding, or trimming |
| `parser_collapse_before_duplicate_detection` | `object_pairs_hook=_ObjectPairs` retains pairs through the complete profile validation |
| `nonstandard_json_constants` | Explicit `parse_constant` rejects NaN and both infinities |
| `logical_validation_begins` | Structural construction and graph/rule validation run only after strict decoding succeeds |
| `decoder_conformance_fixture` | M0 fixture remains validation infrastructure; M1's production entry point is independent |
| `utf8_bom_policy` | Reject leading BOM in bytes or text |
| `decoded_string_policy` | Check keys and values for surrogate code points; valid escaped pairs decode to scalar values |
| `decoded_value_types` | Only objects, arrays, and strings survive profile validation |
| `numbers_booleans_null_policy` | Number callbacks reject without host numeric conversion; bool/null reject before logical validation |

The decoder invokes host `json.loads` with all required strict hooks; it does
not rely on its default duplicate or scalar behavior. `_materialize` executes
only after validation of the entire pair-preserving document. A decoding
failure produces no structural certificate or acceptance result.

## 6. Formula AST, parser, pretty-printer, and surface identity

Authority: `spec/language.yaml`. Implemented constructor fields were compared
directly with the frozen declarations:

| Constructor | Formula-child arity | Payload fields | Status |
| --- | ---: | --- | --- |
| `atom` | 0 | `name` | Primitive, nonempty object-language name |
| `neg` | 1 | `arg` | Primitive |
| `and` | 2 | `left, right` | Primitive |
| `poss` | 1 | `arg` | Primitive |
| `or` | 2 | `left, right` | First-class defined surface node |
| `strict_imp` | 2 | `left, right` | First-class defined surface node |
| `equiv_s` | 2 | `left, right` | First-class defined surface node |

`syntax/formula.py` uses frozen dataclasses, structural equality/hashing, and
closed canonical AST decoding. `atom.name` is a payload, not a child formula.
Schema `{meta: ...}` objects have no object-formula constructor. The trusted
certificate factory wraps malformed AST and unhashable-discriminator failures
as `invalid_formula`.

The operator-specific alias sets and precedence constants were compared
programmatically with the frozen YAML:

| Operator | Precedence / associativity | Accepted aliases |
| --- | --- | --- |
| neg | 90 / prefix | `~`, `¬`, `∼` |
| poss | 90 / prefix | `◇`, `<>` |
| and | 70 / left | `&`, `∧`, `·` |
| or | 60 / left | `\|`, `∨` |
| strict_imp | 40 / right | `⥽`, `strictif` |
| equiv_s | 30 / nonassoc | `≡ₛ`, `equiv_s`, `<=>` |

Recursive-descent parser layers implement these associativities. Parentheses
are explicit; chained unparenthesized equivalence rejects. `=>`, Box,
material implication, object-language `=`, and `:=` syntax are not added.
The small human identifier grammar is narrower than canonical JSON atom names.

No parsing, equality, hashing, substitution, or rule-matching operation erases
defined nodes. `pretty_formula` renders fishhook/equivalence/possibility with
precedence-sensitive parentheses, and supported human formulas round-trip
structurally. `diagnostic_full_erasure` alone recursively follows registered
definitions into the primitive core; no logical checker calls it.

Presentation note: the current readable renderer uses explicit `∧` (the
unambiguous diagnostic form), not a publication-quality Lewis juxtaposition
typesetter. This has no effect on formula identity or proof acceptance.

## 7. Frozen-spec loader and fingerprints

`kernel/frozen_spec.py` loads the four components with a SafeLoader subclass
that rejects duplicate YAML keys. It requires `frozen_m0` and expected version
`0.6`, and checks component/project identity. Version checking uses the
stringified value; it is not a whole-file byte-signature scheme.

The loader checks the exact 12-schema and three-definition domains, recomputes
each schema AST digest and each definition `{lhs, rhs}` digest, and validates
the complete certificate contract against its lock. It additionally pins the
canonical JSON of each entire lock object:

- AST-lock object pin:
  `90d44f404d2dec2407efc4a928777ebc2f080bd7049e1724da706980c39fad3a`.
- Contract-lock object pin:
  `1ea5a56a2a1ecba85c8453cbd5f55af7eb15e32396f9157c85bc36e623939b25`.

Thus editing a contract or AST and only updating its YAML lock is rejected by
this implementation. The contract path and version `1.1` are checked.
The loader resolves exact basis memberships, inheritance, IDs, rule order,
and S5 separation before deep-freezing all returned data.

The entire canonical contract is authenticated; the code does not claim a
bytewise signature over every prose/provenance field of every YAML file.
The Git comparison and M0 validation gates supply the broader repository
non-regression review.

## 8. Closed model and six certificate kinds

Authority header fields `contract_version`, `authority`, `closed_world`, and
`unknown_fields_policy` are covered by the whole-contract lock and closed
structural factory. `metadata_policy` permits no trusted metadata.

Field-set inspection confirmed exact equality between the frozen
`required_fields`/`allowed_fields` and the model fields (including each
justification's constant `kind`):

| Object or kind | Exact field set |
| --- | --- |
| Proof | `proof_id, system, basis_id, goal, root, nodes` |
| Node | `conclusion, justification` |
| postulate_instance | `kind, schema_id, schema_substitution` |
| Sa | `kind, parents, atom_substitution` |
| Sb | `kind, parents, direction, occurrence_path` |
| Ad | `kind, parents` |
| Smp | `kind, parents` |
| definition_conversion | `kind, parents, definition_id, direction, occurrence_path` |

Every `unknown_fields_policy` is rejection. Identifier-policy fields
`proof_id_type`, `node_id_type`, `root_reference_type`,
`parent_reference_type`, `schema_id_type`, `definition_id_type`, and
`node.node_map_key_type` require nonempty strings. `string_identity` and
`reference_resolution` use exact code-point strings without numeric or text
coercion. `system` and `basis_id` are resolved as one exact registered pair.

`certificate.py` implements structural field/type/enum checks.
`checker.py` reuses `transforms.py` for logical checks. Every node conclusion
is validated as an object formula; all declared parents must exist and have
already been accepted in the same session. Parent counts and roles are exact.

### postulate_instance

- `is_lewis_inference_rule: false`; `parent_arity: 0` and no parents field.
- `schema_admission_policy`: schema must be primitive in the declared exact basis.
- `schema_substitution.key_namespace`: schema metavariables, disjoint from atoms.
- `domain_policy`, `missing_keys_policy`, `extra_keys_policy`: exactly the
  metavariable set occurring in the registered schema, without missing/extra keys.
- `value_type`: object formulas without schema metavariables.
- `application_policy`: one simultaneous instantiation; replacements are returned unchanged.
- `conclusion_policy`: exact instantiated surface AST. A direct instance is not Sa.

### Sa

- `is_lewis_inference_rule: true`; `parent_arity: 1`;
  `parent_roles: [source_theorem]`.
- `atom_substitution.key_namespace`: object atom names.
- `domain_policy`: nonempty subset of parent atoms; `extra_keys_policy: reject`.
- `unmentioned_atoms_policy: identity`; `value_type` is object formula.
- `application_policy: simultaneous_one_pass_nonrecursive` and
  `replacement_values_rewritten_by_same_substitution: false`:
  source atoms are visited once; inserted values are not revisited.
- `implicit_definition_conversion: reject` and `conclusion_policy` is exact
  surface result. The p→q, q→r trap rejects its recursive result.

### Sb

- `is_lewis_inference_rule: true`; `parent_arity: 2`;
  `parent_roles: [equivalence_parent, target_parent]`.
- `direction_values`: exactly `left_to_right` or `right_to_left`.
- `equivalence_root_policy`: literal surface `equiv_s`, not its expanded conjunction.
- `selected_occurrence_match_policy`: exact chosen source-side AST.
- `replacement_count: 1`; `root_replacement_allowed: true`.
- `implicit_definition_conversion: reject`; `conclusion_policy`: exact target
  after that one selected replacement, without replace-all behavior.

### Ad

- `is_lewis_inference_rule: true`; `parent_arity: 2`;
  `parent_roles: [left_parent, right_parent]`.
- `conclusion_policy`: exactly `And(left_conclusion, right_conclusion)`.
- `implicit_commutativity_or_reassociation: reject`.
- `implicit_definition_conversion: reject`.

### Smp

- `is_lewis_inference_rule: true`; `parent_arity: 2`;
  `parent_roles: [antecedent_parent, implication_parent]`.
- `implication_root_policy`: literal `strict_imp` on the second parent.
- `antecedent_match_policy`: exact first-parent/antecedent surface identity.
- `conclusion_policy`: exact surface consequent.
- `implicit_definition_conversion: reject`. No material MP or necessitation.

### definition_conversion

- `is_lewis_inference_rule: false`; `parent_arity: 1`;
  `parent_roles: [source_parent]`.
- `direction_values`: exactly `expand` or `contract`.
- `definition_resolution_policy`: only DEF_OR, DEF_STRICT_IMP, DEF_EQUIV_S.
- `metavariable_environment_policy`: one shared environment across matching/output.
- `repeated_metavariable_policy`: exact structural identity.
- `replacement_count: 1` at the supplied occurrence.
- `implicit_additional_conversion` and `implicit_rule_matching_conversion` reject.
- `conclusion_policy`: exact single replacement. The utility does not invoke Sb
  and does not erase newly introduced defined nodes.

## 9. Basis discipline

The single `validate_basis` lookup is shared by structural loading and node
checking. It uses the authenticated immutable basis table:

| System | Exact basis ID | Primitive schema membership |
| --- | --- | --- |
| S1 | `S1_B1_B7` | B1–B7 |
| S2 | `S2_B1_B8` | B1–B8 |
| S3 | `S3_B1_B7_A8` | B1–B7, A8 |
| S4 | `S4_B1_B7_C10` | B1–B7, C10 |
| S5 | `S5_PRIMARY_B1_B7_C11` | B1–B7, C11 |
| S5 | `S5_ALT_B1_B7_C10_C12` | B1–B7, C10, C12 |

No theorem-inclusion hierarchy expands primitive admission. Synthetic union
IDs, cross-system pairs, whitespace/case aliases, and cross-session accepted
parents do not supply evidence. S5 bridge metadata is preserved but there is
no bridge certificate kind, macro interpreter, or bridge theorem library.

## 10. Occurrence paths

Every field of `canonical_certificate_contract.occurrence_path` is implemented:

- `payload_type` is a list of strings at serialization, frozen to a tuple in models.
- `root` is `[]`.
- `legal_segments` is exactly `arg, left, right`.
- `traversable_fields` is empty for atom; `arg` for neg/poss;
  `left, right` for and/or/strict_imp/equiv_s.
- `unknown_segments_policy` rejects.
- `definition_expansion_during_traversal` is forbidden.

`_path` validates grammar; `_locate` resolves one surface subtree;
`replace_occurrence` rebuilds only its ancestor chain. Shared Python subtree
objects do not cause multiple visible occurrences to be replaced.
`atom.name` is never traversable. Schema matching and definition conversion
use exact repeated-metavariable environments, not syntactic/semantic erasure.

## 11. Whole-DAG checker and deterministic ordering

`kernel/dag.py` implements all fields of `canonical_certificate_contract.dag`:

| Frozen invariant | Implementation |
| --- | --- |
| `node_ids_unique` | Recursive duplicate-name decoder plus nonempty string structural IDs |
| `all_references_must_resolve` | Root lookup and every ordered parent reference checked before traversal |
| `acyclic` | Iterative DFS active stack; deterministic closed cycle witness |
| `all_nodes_reachable_from_root` | Follow dependencies from root; reject all extra nodes, even valid theorems |
| `parents_accepted_before_child` | Deterministic DFS postorder passed to the six-kind NodeChecker |
| `proof_formulas_forbid_schema_metavariables` | Closed formula AST decoder and exact-constructor validation |
| `root_conclusion_exactly_equals_goal` | Final exact structural equality, with no erasure |
| `line_numbers_are_nonnormative_renderer_output` | Node-order tuple contains original IDs; rendering alone allocates line numbers |

DFS starts in code-point ID order and traverses edges in declared parent order.
Repeated parent references are legal edges, not duplicate nodes. A 1,500-node
chain tests iterative traversal. Logical nodes are checked once, after their
parents. Failed checks cannot add a node to the accepted ledger.

Error precedence is strict decode, closed structure, root/reference checks,
cycles, reachability, logical checks in stable topological order, then goal
equality. Structural node validation is sorted for diagnostics while the
structural model preserves input mapping order. Decoder errors follow
serialized order; graph/rule diagnostics are independent of JSON object order.

## 12. Renderer and trust boundary

`render.py` consumes `CheckedCertificate` and calls the surface pretty-printer.
It preserves `⥽`, `≡ₛ`, `◇`, registered B/A/C labels, Sa/Sb/Ad/Smp, and explicit
Df labels for definition conversions. Parent references retain their logical
order while being translated to display line numbers.

No kernel acceptance function imports or calls the renderer. The tests alter
or break rendering and offset line numbers without changing acceptance.
Unsupported human atom names receive explicit surface-JSON fallback text,
not implicit logical conversion. Rendering output itself is not a canonical
certificate input. There is no default erased rendering.

## 13. Error taxonomy

`CertificateValidationError` exposes stable `code`, `detail_code`, `node_id`,
`kind`, `reason`, and `related_ids`. Tests rely on those fields, not only prose:

```text
document_decode_error
closed_world_field_error
invalid_formula
invalid_basis
invalid_identifier
invalid_structure
missing_root
missing_parent
cycle
unreachable_node
invalid_postulate_instance
invalid_Sa
invalid_Sb
invalid_Ad
invalid_Smp
invalid_definition_conversion
root_goal_mismatch
validation_capacity_error
```

Low-level typed families include `FrozenSpecError` and its status, version,
format, fingerprint, basis, and contract subclasses; document encoding,
duplicate-key, string, scalar-type, constant, and top-level errors; structural
field/identifier/basis/formula errors; formula parse/AST/print/erasure errors;
and schema/substitution/path/conversion transform errors.

`NodeCheckError` retains node/kind and finer reasons such as
`SCHEMA_ADMISSION`, `CONCLUSION_MISMATCH`, `SB_EQUIVALENCE_ROOT`, and
`SMP_ANTECEDENT`. Public checker failures are not generic assertions.
CLI-only operational codes are `help_requested`, `usage_error`,
`frozen_spec_error`, `certificate_io_error`, and `internal_error`.

## 14. Complete test inventory and counts

Collection and execution both cover **958 tests**: 44 existing M0 tests and
914 M1 tests. The dedicated Prompt 08 suite contributes 134 tests, including
35 CLI tests.

| Test file | Count |
| --- | ---: |
| `tests/kernel/test_basis.py` | 25 |
| `tests/kernel/test_certificate_document.py` | 87 |
| `tests/kernel/test_certificate_structure.py` | 169 |
| `tests/kernel/test_checker_a.py` | 138 |
| `tests/kernel/test_checker_b.py` | 72 |
| `tests/kernel/test_dag.py` | 91 |
| `tests/kernel/test_frozen_spec.py` | 11 |
| `tests/kernel/test_transforms.py` | 125 |
| `tests/m1/test_adversarial.py` | 99 |
| `tests/m1/test_cli.py` | 35 |
| `tests/spec/test_bridge_and_provenance.py` | 5 |
| `tests/spec/test_certificate_document_boundary.py` | 12 |
| `tests/spec/test_closed_serialization.py` | 5 |
| `tests/spec/test_core_spec.py` | 7 |
| `tests/spec/test_fingerprint_lock.py` | 3 |
| `tests/spec/test_second_closure_mutations.py` | 10 |
| `tests/spec/test_yaml_loader.py` | 2 |
| `tests/syntax/test_formula.py` | 62 |
| **Total** | **958** |

Six checked-in JSON fixtures are complete, minimal regression certificates
for their root kind: postulate_instance (1 node), Sa (2), Sb (6), Ad (3),
Smp (3), definition_conversion (2). They are synthetic checking fixtures,
not historical theorem claims.

## 15. Adversarial and mutation coverage

Implementation-facing rejection tests cover:

- top-level/nested/escape-equivalent duplicate names; invalid/overlong UTF-8;
  BOM; surrogate keys/values; NaN/infinities; numbers, booleans, null;
  non-object input; closed unknown fields;
- hidden Box/material implication/equality; wrong arities; schema metavariables
  in object formulas; defined-versus-expanded surface confusion;
- B8 in S1, A8 in S2, C11 in S5 alternative, C10/C12 in S5 primary, unions,
  invalid pairs, and cross-session parent trust;
- missing/extra or wrong-namespace schema keys; recursive/sequential Sa traps;
  bad paths and atom.name traversal; multiple selected occurrences;
  inconsistent definition environments and hidden second conversions;
- wrong parent count/order; expanded mutual implications as Sb premise;
  reversed/reassociated Ad; Smp erasure-only antecedent match;
  hidden modern-rule or bridge-kind claims;
- missing/empty/coerced IDs, cycles including disconnected components,
  unreachable garbage, root-goal mismatch, deterministic ordering and diagnostics;
- renderer/line-number changes and strict CLI error/exit behavior.

The dedicated mutation suite checks the intended error category, avoiding
false success caused by an unrelated unreachable-node or malformed-parent
failure. Temporary copied M0 bundles are used for loader rejection tests;
real frozen files are not mutated.

Coverage 7.16.0 measured the in-process `lewis_prover.kernel` package with
branches enabled: **768/813 statements (94.46%)**, **276/310 branches (89.03%)**,
**92.97% combined** (rounded to 93% by the report).
Subprocess CLI execution is not included in those coverage counters.
Coverage is not certification or a completeness proof. Remaining paths are
largely defensive malformed-input/resource guards and checks whose antecedents
are prevented by the authenticated frozen registry. No frozen contract was
relaxed to inflate coverage.

## 16. CLI behavior

`python -m lewis_prover verify <certificate.json>` authenticates the frozen
bundle, reads certificate bytes, strictly decodes, and invokes the complete
checker. `--spec-root` defaults to the current directory, without fallback.
Only the verify command is registered; there is no prove command.

Every invocation emits a status followed by sorted-key JSON detail:

- `VALID_CERTIFICATE` and exit 0 only for acceptance.
- `INVALID_CERTIFICATE` and exit 1 for a rejected certificate.
- `INVALID_CERTIFICATE` and exit 2 for help/usage, frozen-spec, I/O, or internal
  failure. Help is returned in JSON and cannot produce a false success exit.

Success details identify proof/system/basis/root/node count. Rejection details
preserve structured checker diagnostics. No rendering is required for validity.

## 17. Commands run and exact results

Environment: Python 3.12.3, pytest 8.4.2, PyYAML 6.0.3. All Python commands
below used the repository's `.venv/bin/python`, i.e. the explicit virtual-
environment equivalent of `python`.

| Command or probe | Result |
| --- | --- |
| `git rev-parse m0-foundational-spec-v1` | `3ded752aef28be17509649fbcd47a3daf29c7279` |
| `git show --stat --oneline m0-foundational-spec-v1` | One added certification report, 258 lines |
| Tagged four-spec status probe | **Exit 1: FROZEN_BASELINE_GATE FAIL**, all four values `candidate_m0` |
| Parsed Git/YAML comparison against both 21117f3 and 3ded752 | Exit 0; four status-only spec differences; exact allowed audit-accounting paths |
| Raw lock comparison and canonical contract digest recomputation | Exit 0; hashes in section 2 match |
| Model/AST/operator field probe | Exit 0; all seven fields/arities, six alias/precedence sets, proof/node/six-kind field sets match |
| `git ls-files '*:Zone.Identifier'` | Exit 0; empty output |
| `.venv/bin/python -m pip install --no-cache-dir -e '.[dev]'` | Exit 0 on approved network retry; editable package 0.0.0 built/installed |
| `.venv/bin/python -m pip check` | Exit 0; `No broken requirements found.` |
| `bash scripts/run_m0_checks.sh` | Exit 0; spec validation PASS, source-register validation PASS, both freeze-readiness checks PASS, 958 passed |
| `.venv/bin/python -m pytest` | Exit 0; 958 passed |
| `.venv/bin/python -m pytest --collect-only -q` | Exit 0; inventory in section 14 |
| `.venv/bin/python -m coverage run --branch --source=lewis_prover.kernel -m pytest` | Exit 0; 958 passed |
| `.venv/bin/python -m coverage report` | Exit 0; 813 statements, 45 missed; 310 branches, 32 partial; 93% combined |
| `git diff --check` | Exit 0; no whitespace errors |
| Source/untracked-file trailing-whitespace scan | No matches |
| Log completeness probe | Exit 0; all 43 obligation IDs, all 39 pre-existing M1 additions, 21 sections, correct failed-gate ending |
| `git status --short` | Pending administrative modifications and untracked M1 files; not a clean committed candidate |

The validation script runs these four required commands before pytest:

```bash
.venv/bin/python scripts/validate_spec.py
.venv/bin/python scripts/validate_source_register.py
.venv/bin/python scripts/validate_spec.py --freeze
.venv/bin/python scripts/validate_source_register.py --freeze
```

CLI smoke commands, with no PYTHONPATH override after the editable installation:

```bash
for kind in postulate_instance Sa Sb Ad Smp definition_conversion; do
  .venv/bin/python -m lewis_prover verify "tests/fixtures/m1/$kind.json" || exit
done
```

Result: six `VALID_CERTIFICATE` statuses, each exit 0; counts are listed in
section 14. Four temporary negative fixture files were generated without
editing the checked-in fixtures, under `/tmp/lewis-m1-final-WK5KG6`:

| Command suffix after `.venv/bin/python -m lewis_prover verify` | Exact result |
| --- | --- |
| `/tmp/lewis-m1-final-WK5KG6/duplicate-key.json` | Exit 1; INVALID_CERTIFICATE; `document_decode_error` / `DuplicateCertificateKeyError` |
| `/tmp/lewis-m1-final-WK5KG6/invalid-basis.json` | Exit 1; INVALID_CERTIFICATE; `invalid_basis` / `CertificateBasisError` |
| `/tmp/lewis-m1-final-WK5KG6/invalid-rule.json` | Exit 1; INVALID_CERTIFICATE; `invalid_Sa` / `CONCLUSION_MISMATCH`; node `root` |
| `/tmp/lewis-m1-final-WK5KG6/invalid-dag.json` | Exit 1; INVALID_CERTIFICATE; `cycle`; witness `["root", "root"]` |

Reproduction recipes: duplicate the postulate fixture's top-level root member;
change its system/basis to S5 and the synthetic union ID; change the Sa
fixture's root conclusion/goal to atom `wrong`; or make the Sa root depend on
itself. These expected exit-1 rejections are successful negative tests, not
failed gates.

Transient verification setup failures were not suppressed: an initial
`--no-build-isolation --no-deps` editable-install attempt exited 2 because
`setuptools.build_meta` was absent; the ordinary isolated-install attempt
initially exited 1 under sandbox network restrictions, then succeeded with
approval. An initial ad-hoc arity probe incorrectly counted atom.name as a
formula child; correcting the probe to arity zero passed without changing
production code. None of these resolves the still-failed frozen-baseline gate.

## 18. Forbidden shortcuts inspected and confirmed absent

Source inventory, import/call review, and `rg` searches of `src` and regression
tests confirmed no trusted acceptance path for:

- proof search or a prove command;
- derived-rule acceptance or historical theorem-library lookup;
- trusted theorem caches or imported accepted-parent ledgers;
- semantic validity or truth-table/model/algebraic oracles;
- Kripke, tableau, sequent, or natural-deduction acceptance;
- unrestricted necessitation;
- material implication or material modus ponens;
- implicit definition unfolding/contraction or full-erasure rule equality;
- mixed S5 primitive union or automatic theorem-inclusion admission;
- S5 bridge macro acceptance;
- permissive first-wins/last-wins certificate parsing or YAML certificate input;
- direct use of rendered line numbers as logical references;
- trusted renderer output, hidden certificate metadata, or schema holes in object formulas.

The only production JSON decoding call is the strict, pair-preserving one in
`kernel/document.py`. Test-fixture `json.loads` calls do not accept proofs.
The YAML call belongs only to the frozen-spec loader. Diagnostic erasure is
exported for explicit use but not invoked by the logical checker. “Union,”
“bridge,” and modern-rule names found in tests are rejection cases or comments,
not acceptance branches. No source-tree eval/exec-based proof acceptance exists.

No trusted-shortcut blocker was found. M1-GATE-01 is a distinct provenance
blocker, not evidence of a changed Lewis calculus.

## 19. Known limitations and remaining work

1. **Required release gate remains failed:** the intended M0-freeze tag does
   not contain frozen statuses. Resolve/document that history before presenting
   an M1 candidate. This log cannot retroactively establish the required order.
2. No final candidate SHA or candidate-specific remote CI result is available.
   The M0 certification report concerns its exact M0 anchor, not M1.
3. Python/dataclasses, standard JSON, PyYAML loading, and hashing belong to the
   computing base. This is not a proof of verifier correctness or a sandbox
   against hostile Python code mutating module internals.
4. Direct model/structural constructors are not whole-proof acceptance APIs.
   They do not prove that an earlier external decoder preserved duplicate keys.
5. Some formula/JSON operations remain recursive. Capacity failures reject or
   fail closed; there is no comprehensive CPU/memory quota system. Iterative
   DAG traversal does not remove formula-depth limits.
6. Human notation intentionally covers a smaller atom-name language than JSON.
   Rendering is readable surface/diagnostic text, not complete article typesetting.
7. AST/contract locks and exact basis pins are authenticated; every prose field
   of the YAML bundle is not individually hashed by the runtime loader.
8. S1/A-series normalization certificates, S4 inclusion proofs, both S5 bridge
   derivations, the historical corpus, proof search, and premise consequence
   are later work, not silently admitted shortcuts or unfinished M1 rules.
9. The existing M0 workflow runs all tests when triggered, but its path filters
   do not independently include `src/**` or all new M1-only test paths. This
   candidate changes pyproject.toml, which is included. Future source-only
   change coverage needs explicit CI follow-up; no workflow was silently edited.
10. The original package manifest is not an inventory of the new M1 source
    tree. Section 3 supplies the exact candidate inventory; setuptools discovers
    the package independently.

There is no known missing requested node kind, document profile check, basis
check, DAG invariant, verifier CLI, or adversarial fixture within Prompts 01–08.
That local implementation assessment does not waive M1-GATE-01 or constitute
independent audit.

## 20. Scope statement

M1 implements checking only; proof search is not implemented.

## 21. Frozen-obligation to implementation/test mapping

The following maps every one of the 43 registered M0 obligations. Source
verification itself is not repeated or newly certified here. Deferred bridge
and historical machine certificates stay deferred.

| Obligation(s) | Frozen authority / meaning | M1 implementation | Verification evidence |
| --- | --- | --- | --- |
| M0-L01 | language formula/operator registry | `syntax/formula.py`, `parser.py`, `pretty.py` | `tests/syntax/test_formula.py`; field/alias probe |
| M0-D01 | DEF_OR / 11.01 | `transforms.convert_definition`, diagnostic `erasure.py` | `test_transforms.py`, `test_checker_a.py` |
| M0-D02 | DEF_STRICT_IMP / 11.02 | Same, with preserved fishhook constructor | `test_formula.py`, `test_transforms.py`, definition fixture |
| M0-D03 | DEF_EQUIV_S / 11.03 and Sb | `formula.EquivS`, `transforms.py`, `checker.py` | `test_checker_a.py`, `test_checker_b.py`, Sb fixture |
| M0-D04 | Explicit conversion, diagnostic erasure only | `checker.py`, `transforms.py`, `syntax/erasure.py` | Surface/erasure traps in formula, transform, checker and M1 adversarial tests |
| M0-R01 | Project labels versus provenance | `certificate_model.py`, `render.py` | Six-kind/render tests; frozen provenance unchanged |
| M0-R02 | Sa theorem-mode substitution | `transforms.substitute_atoms`, `checker.NodeChecker` | `test_transforms.py`, `test_checker_a.py`, Sa fixture |
| M0-R03 | Sb one-occurrence theorem replacement | `transforms.resolve_occurrence/replace_occurrence`, `checker.py` | `test_checker_b.py`, `test_adversarial.py` |
| M0-R04 | Ordered two-parent Ad | `checker.py` | `test_checker_b.py`, Ad fixture |
| M0-R05 | Native strict detachment | `checker.py` | `test_checker_b.py`, Smp fixture |
| M0-A01 | B1–B7 ASTs | `frozen_spec.py`, `transforms.instantiate_schema` | Pinned hashes; `test_transforms.py`, `test_checker_a.py` |
| M0-A02 | B8 AST | Same; exact basis admission | `test_basis.py`, `test_checker_a.py`, `test_adversarial.py` |
| M0-A03 | A8 AST | Same; normalized S3 admission | Same basis/schema tests |
| M0-A04 | C10 AST without Box | Same | Frozen fingerprints and S4/S5 basis tests |
| M0-A05 | C11 AST without Box | Same | Primary/alternative rejection tests |
| M0-A06 | C12 AST without Box | Same | Alternative/primary rejection tests |
| M0-N01 | No duplicate A1–A7 primitive registry | `frozen_spec.py` exact schema domain | `test_frozen_spec.py`, `test_checker_a.py`; source wording unchanged |
| M0-N02 | S3 = normalized S1 + A8 | `frozen_spec.py`, `basis.py` | Exact admission tests; historical equivalence certificate deferred |
| M0-S01 | S1 B1–B7 | `basis.py`, `frozen_spec.py`, `checker.py` | `test_basis.py`, `test_checker_a.py` |
| M0-S02 | S2 B1–B8 | Same | Same |
| M0-S03 | S4 B1–B7+C10 | Same | Same |
| M0-S04 | Two separate S5 bases | Same | Both S5 primitive-set/union rejection suites |
| M0-B01 | S4 inclusion not blind primitive inheritance | `basis.py` / no inclusion kind | `test_checker_b.py`; native library proof deferred |
| M0-B02 | S5 basis equivalence | No bridge macro accepted | `test_basis.py`, `test_checker_b.py`; both machine derivations deferred |
| M0-E01 | B9 and existence machinery excluded | Exact schema/constructor domains | `test_transforms.py`, `test_formula.py`; frozen exclusion preserved |
| M0-C01 | Explicit Df certificate nodes | `certificate_model.py`, `certificate.py`, `checker.py` | `test_checker_a.py` and definition fixture |
| M0-C02 | Postulate instantiation is not Sa | Separate model/dispatch; `transforms.py` | `test_checker_a.py`, `test_adversarial.py` |
| M0-C03 | One shared occurrence-path grammar | `certificate.py`, `transforms.py` | `test_transforms.py`, Sb/definition rejection suites |
| M0-C04 | Exact S5 basis identity | `basis.py`, `checker.py`, `dag.py` | `test_basis.py`, `test_dag.py` |
| M0-V01 | Freeze-readiness validation | Runtime `frozen_spec.py` plus unchanged M0 scripts | Four PASS validators; **Git baseline gate separately failed** |
| M0-CI01 | Governing-file CI coverage | Existing workflow unchanged | Workflow inspection; local full suite; path-filter limitation above |
| M0-H01 | No tracked Zone.Identifier | No runtime feature | Empty `git ls-files '*:Zone.Identifier'` output |
| M0-C05 | Closed fields and exact string references | `document.py`, `certificate.py`, `dag.py` | `test_certificate_structure.py`, `test_dag.py`, `test_adversarial.py` |
| M0-B03 | Operational S5 bridge direction | Frozen records preserved; no expansion implementation | Whole-system Git equality; unchanged `test_bridge_and_provenance.py` |
| M0-P02 | Precise Parry provenance | No reinterpretation in runtime | Entire non-status spec/source metadata comparison |
| M0-V02 | Semantic mutation rejection | `frozen_spec.py`, `transforms.py`, `checker.py` | M0 mutation suite plus M1 implementation attacks |
| M0-DOC02 | One-element parents list, not parent | `certificate_model.py`, `certificate.py` | `test_certificate_structure.py` and kind fixtures |
| M0-FP02 | Lock metadata authentication | `frozen_spec.py` entire-lock pins | `test_frozen_spec.py`, unchanged `test_fingerprint_lock.py` |
| M0-V03 | Sole certificate authority | `certificate.py` / contract-backed checks | Lock comparison, forbidden-registry and source review |
| M0-FP03 | Complete contract fingerprint | `frozen_spec.py` | Contract/lock mutation tests and exact digest recomputation |
| M0-C06 | Strict canonical document boundary | `document.py` | `test_certificate_document.py`, `test_adversarial.py`, CLI duplicate smoke |
| M0-V04 | Recursive duplicate-key conformance | `document.py`, `dag.py` | Existing 12 M0 boundary tests plus M1 decoder/CLI suites |
| M0-FP04 | M0.6 full contract lock | `frozen_spec.py` | Immutable lock bytes; complete contract hash; pending baseline finding |

File-by-file production ownership (paths relative to `src/lewis_prover/`):

| File | Responsibility / obligations | Principal tests |
| --- | --- | --- |
| `__init__.py` | Public initialization surface; M0-V01 | `test_frozen_spec.py` |
| `__main__.py` | Verifier-only entry point; M0-C06 | `test_cli.py` |
| `cli.py` | Authenticate/decode/check/status orchestration; M0-V01/C06 | `test_cli.py` |
| `errors.py` | Typed diagnostic boundary across M0-C05/C06/V02 | All rejection suites |
| `kernel/__init__.py` | Explicit public kernel exports; M0-V03 | Kernel imports throughout suite |
| `kernel/model.py` | Frozen immutable spec/basis views; M0-V01/FP02 | `test_frozen_spec.py` |
| `kernel/frozen_spec.py` | Lock/AST/basis authentication; M0-A01–A06/FP02–FP04/S01–S04 | `test_frozen_spec.py`, copied-spec CLI tests |
| `kernel/basis.py` | Exact system/basis lookup; M0-C04/S01–S04 | `test_basis.py` |
| `kernel/document.py` | Strict decoded profile; M0-C05/C06/V04 | `test_certificate_document.py` |
| `kernel/certificate_model.py` | Six closed immutable data shapes; M0-C01/C02/C05/DOC02 | `test_certificate_structure.py` |
| `kernel/certificate.py` | Contract-driven structural factory; M0-C05/C06 | `test_certificate_structure.py`, `test_adversarial.py` |
| `kernel/transforms.py` | Schema/atom substitution, paths, explicit definitions; M0-D01–D04/R02/R03/C03 | `test_transforms.py` |
| `kernel/checker.py` | Six native node checks; M0-R02–R05/C01/C02/C04 | `test_checker_a.py`, `test_checker_b.py` |
| `kernel/dag.py` | Complete DAG acceptance; M0-C05/C06/V02 | `test_dag.py` |
| `syntax/__init__.py` | Formula API; explicit diagnostic erasure export; M0-D04 | `test_formula.py` |
| `syntax/formula.py` | Seven surface constructors; M0-L01/D03/D04 | `test_formula.py`, structure tests |
| `syntax/parser.py` | Frozen human aliases/precedence; M0-L01/D02 | `test_formula.py` |
| `syntax/pretty.py` | Surface notation and parentheses; M0-L01/D02/D03 | `test_formula.py` |
| `syntax/erasure.py` | Diagnostic registered expansion only; M0-D04 | `test_formula.py`, erasure traps |
| `render.py` | Untrusted labels/Df/line numbers; M0-R01/C01/C02 | Renderer tests in `test_dag.py` |

`tests/m1/conftest.py` loads fresh regression fixtures; the six JSON files
exercise the corresponding rows above; their README documents reproduction.
`pyproject.toml` supplies packaging/test discovery, not certificate semantics.
This log records review evidence and the failed provenance gate; it is not an
additional semantic authority.

M1 IMPLEMENTATION NOT COMPLETE
