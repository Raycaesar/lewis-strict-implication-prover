# M1 frozen-spec integrity inventory

## Second-repair Python entry-point inventory

Inspected before implementation against failed first closure candidate
`b5d543db60ed7631f9e182f137ce2f83156d2ec3`. The file-loader boundary below
was closed; its protection did **not** extend to caller-constructed models.
This table records the missing checks and the required second-repair boundary.

| Entry point | Accepted spec/basis input | Trusted acceptance-sensitive? | Validation at b5d543 | Required validation |
| --- | --- | --- | --- | --- |
| `load_frozen_spec` | Root containing the six frozen files | Yes, authority initialization | Complete file manifest plus metadata, AST/contract locks and normalized-basis checks | Retain every gate before constructing the immutable authority; do not skip file validation on subsequent loads |
| `validate_frozen_spec` (new) | `FrozenSpec`, including reconstructed fields and `bases: Mapping[str, FrozenBasis]` | Yes, common boundary | Absent | Compare all semantic fields and every derived basis field to the authenticated authority; return only the authority's immutable snapshot |
| `check_certificate` | Serialized certificate and `FrozenSpec` | Yes, whole-proof acceptance | Passed supplied spec directly to loading and checking | Validate spec before certificate work; use returned snapshot throughout |
| `load_certificate` | Serialized certificate and `FrozenSpec` | Yes, trusted structural loading; no theorem acceptance | Strict JSON decoder, then unchecked spec-dependent structure loading | Validate spec before decode/structure; preserve strict JSON behavior |
| `certificate_from_document` | Decoded document and `FrozenSpec` | Yes, spec-dependent model construction; no serialized/theorem acceptance | Document value checks; unchecked contract and derived basis | Validate spec before reading the contract or resolving a basis |
| `NodeChecker.__init__` | Structural certificate and `FrozenSpec` | Yes, incremental acceptance session | Certificate class check; stored caller spec | Validate spec and retain only the authority snapshot |
| `NodeChecker.check_node` | Node ID; session-held spec/basis-dependent state | Yes, incremental acceptance | Used stored spec, unchecked contract and basis mapping | Ensure the stored spec passes the same boundary before any node work; all parents use that fixed authority |
| `validate_basis` | System/basis ID and `FrozenSpec.bases` | Yes, primitive admission | Checked ID pair only, trusted caller-derived basis contents | Authenticate entire spec and derived table, then return the authority's exact basis |
| `schema_metavariables`, `instantiate_schema`, `match_schema` | Schema ID, formulas/environment, `FrozenSpec` | Yes, supported trusted transforms | Used caller schema ASTs and constructor fields | Validate at each public entry; private matching/instantiation use only the returned snapshot |
| `object_atom_names`, `substitute_atoms` | Formulas/environment and `FrozenSpec` | Yes, Sa-dependent transforms | Used caller occurrence traversal contract | Validate at each public entry before traversal |
| `resolve_occurrence`, `replace_occurrence` | Formulas/path and `FrozenSpec` | Yes, Sb/conversion-dependent transforms | Used caller path grammar and traversal contract | Validate at each public entry before traversal |
| `convert_definition` | Formula, definition ID, direction/path, `FrozenSpec` | Yes, definition conversion | Used caller definitions, constructor fields and contract | Validate before definition lookup, matching or instantiation |
| Private transform helpers `_children`, `_check_formula`, `_schema`, `_environment`, `_instantiate`, `_match`, `_path`, `_locate` | Snapshot plus derived patterns/environments | Yes, internally | Relied on the unenforced public loader precondition | Explicit internal-only helpers; every supported caller validates first; no public API accepts externally prepared pattern/constructor state |
| `FrozenSpec`, `FrozenBasis`, `deep_freeze` | Caller data and nested containers | Data builders only | Dataclass freezing was shallow; documentation implied authentication | Explicitly confer no trust; no checking API consumes a standalone basis; all derived fields are validated through the owning spec |
| `diagnostic_full_erasure` / private `_expand_root` | Formula and `FrozenSpec` | No, diagnostic only; never called by checking | Unchecked definition links | Apply the common spec boundary for consistent public behavior; remains diagnostic only |
| `decode_certificate_document`, formula/parser/pretty APIs, certificate models, `linearize`, renderer, CLI | No direct spec/basis input (CLI obtains spec through loader) | Decoder and fixed formula structure are trusted; rendering is not acceptance | Fixed JSON/formula rules; CLI uses authenticated loader | No new semantic input boundary; preserve these APIs and CLI flow |

The comparison covers complete `language`, `rules`, `schemas`, `systems`, the
separately exposed `canonical_certificate_contract`, `spec_version`, and the
complete derived `bases` table. Only `repository_root` is location metadata;
it cannot authenticate data. List/tuple and set/frozenset representations may
be equivalent, but scalar types, mapping domains, sequence order, every basis
ID/membership/rule/alternative flag and all definition links must agree.
No boolean, provenance text, copied digest or validation marker grants trust.

Implemented in `kernel.frozen_spec.validate_frozen_spec`. Every entry above
uses its return value: the recursively immutable snapshot initialized only
after the unchanged complete-file loader gates pass. The validator compares
all data structurally, including exact scalar types and every `FrozenBasis`
field, and never retains a caller's mappings. The reference consists only of
the existing authenticated YAML and its derived bases; no second semantic
registry was added. Subsequent explicit file loads still authenticate every
input even when the in-memory authority is initialized. New tests cover all
15 public spec-using entry points (including the validator and diagnostic
erasure), the incremental session's retained state, and every semantic
component; 299 API cases and the 69 published file-mutation classes pass.

## First-repair file-loader inventory (historical scope)

Scope: every specification read in `src/lewis_prover/kernel/**` and
`src/lewis_prover/syntax/**`, traced from failed M1
`e0837632aa9e187ccbc5a6fcc1a3a8816e17fe56` (identical replay `d87f114`).
This is a review inventory, not an executable semantics registry. Paths below
refer to YAML fields; `contract` abbreviates only
`spec/rules.yaml#canonical_certificate_contract`.

“Before” means integrity validation in the audited loader, not validation by
the separate M0 scripts. “After” includes the mandatory complete-file SHA-256
gate in the first M1 repair's **file loader only**. Caller-created Python
objects were not covered, as the closure audit subsequently demonstrated.
“Acceptance-sensitive” includes inputs used by initialization to
admit/reject a baseline. Fields implemented as fixed Python behavior rather
than read at runtime are identified separately.

| Field | Consumer | Acceptance-sensitive? | Before integrity-validated? | After integrity-validated? |
| --- | --- | --- | --- | --- |
| All four spec files: `status`, `spec_version`, `component`, `project` | `frozen_spec._validate_component_metadata` | yes | yes, exact metadata checks | yes, checks + complete-file digest |
| `language.formula_ast.{neg,and,poss,or,strict_imp,equiv_s}.fields`, including order and full list membership | `transforms._match`, `_instantiate`; transitively schema matching/instantiation and both directions of definition conversion | yes | **no** | yes, complete `language.yaml` blob |
| `language.formula_ast.atom.fields` | Atom branches in matching/instantiation and `syntax.formula` use fixed `name` behavior; no runtime read of this declaration | no dynamic influence; frozen constructor contract protected | **no** | yes, complete blob |
| `language.formula_ast.*.arity`, `primitive`, `object_level`, `first_class_surface_node` (where present) | Fixed constructor types and field shapes in `syntax.formula`; no runtime read of these declarations | no dynamic influence; frozen constructor contract protected | **no** | yes, complete blob |
| `language.formula_ast.{or,strict_imp,equiv_s}.definition_id` | `syntax.erasure._expand_root` | no, diagnostic erasure only | **no** | yes, complete blob |
| `language.formula_ast` operator membership | `syntax.erasure._expand_root`; non-atom lookup in `transforms._match` / `_instantiate` | yes for trusted lookups | **no** | yes, complete blob |
| `language.metadefinitions` definition-ID membership | `frozen_spec._validate_ast_lock`, `transforms.convert_definition`, `syntax.erasure._expand_root` | yes | yes, exact ID domain | yes + complete blob |
| `language.metadefinitions.*.{lhs,rhs}` and every nested `op`, `meta`, `name`, child AST | `_validate_ast_lock`; `transforms._match`, `_instantiate`; diagnostic erasure | yes | yes, certified AST hashes | yes + complete blob |
| `schemas.schemas` schema-ID membership | `_validate_ast_lock`, `transforms._schema` | yes | yes, exact ID domain | yes + complete `schemas.yaml` blob |
| `schemas.schemas.*.ast`, including all nested pattern fields | `_validate_ast_lock`; `_schema`, `_metavariables`, `_match`, `_instantiate`, `schema_metavariables` | yes | yes, certified AST hashes | yes + complete blob |
| `rules.canonical_certificate_contract` entire object and `contract_version` | `_validate_contract`; exposed immutable contract | yes | yes, whole-contract hash and version | yes + complete `rules.yaml` blob |
| `contract.{top_level,node}.{required_fields,allowed_fields}` | `certificate._fields`, `certificate_from_document` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.kinds` membership | `certificate._justification`, structural diagnostics, `checker.NodeChecker.check_node` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.kinds.*.{required_fields,allowed_fields}` | `certificate._justification` / `_fields` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.kinds.*.parent_arity` | `certificate._justification`, `checker.NodeChecker.check_node` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.kinds.{Sb,definition_conversion}.direction_values` | `certificate._justification`, `checker.NodeChecker.check_node`, `transforms.convert_definition` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.kinds.Sb.root_replacement_allowed` | `checker.NodeChecker.check_node` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.occurrence_path.legal_segments` | `certificate._justification`, `transforms._path` | yes | yes, whole-contract hash | yes + complete blob |
| `contract.occurrence_path.traversable_fields.{atom,neg,and,poss,or,strict_imp,equiv_s}` | `transforms._children`; `_check_formula`, `_locate`, `resolve_occurrence`, `replace_occurrence`, `object_atom_names`, `substitute_atoms`; Sb and definition conversion | yes | yes, whole-contract hash | yes + complete blob |
| `systems.systems` system-ID membership | `_validate_bases` / `_resolve_schemas` | yes | yes, exact ID set | yes + complete `systems.yaml` blob |
| `systems.systems.S1..S4.normalized_basis.{basis_id,inherit_schemas_from,schemas,add_schemas,rules}` (fields where present) | `_basis_block`, `_resolve_schemas`, `_validate_bases`; after repair `_build_bases` | yes | yes for resolved schema/rule/ID results; **no** exact declaration identity | yes, exact complete blob + existing resolved checks |
| `systems.systems.S5.{primary_normalized_basis,alternative_normalized_basis}` same fields | Same basis consumers | yes | yes for resolved results; **no** exact declaration identity | yes, exact complete blob + resolved checks |
| `systems.systems.S5.proof_basis_policy.{union_forbidden,allowed_basis_ids}` | `_validate_bases` | yes | yes, exact checks | yes + complete blob |
| `systems.certificate_basis_policy.system_basis_ids` | `_validate_bases` | yes | yes, exact mapping | yes + complete blob |
| `audit/m0/certified_ast_fingerprints.yaml` entire parsed object, `schema_ast_sha256`, `metadefinition_ast_sha256` | `_validate_ast_lock` | yes | yes, pinned lock-object hash and AST comparisons | yes + raw blob digest |
| `audit/m0/certificate_contract_lock.yaml` entire parsed object, `contract_path`, `contract_version`, `canonical_contract_sha256` | `_validate_contract` | yes | yes, pinned lock-object hash and contract comparison | yes + raw blob digest |
| Other fields in all six input files, including constructor notes, schema/definition provenance and display metadata, source policy, bridge records, normalization prose | Copied by `deep_freeze`, not interpreted by certificate acceptance | no | no complete-file identity check; some are inside already hashed subobjects | yes, every byte |

Derived `FrozenSpec.bases[*].{system_id,schemas}` are consumed by
`basis.validate_basis` and `checker.NodeChecker.check_node`; IDs are mapping
keys. `rules` and `alternative` are authenticated basis metadata. They are
constructed by the loader only after all file identities pass. Ordinary
caller construction had no such gate in b5d543; the new API validator now
checks every derived field and returns the authority's own basis data.
`FrozenSpec.repository_root`
is caller location metadata, not semantics; `spec_version` is the checked M0
version. `kernel.model`, `certificate_model`, `dag`, and package initializers
have no further dynamic specification inputs beyond the Python spec boundary
inventoried above. File reads are confined to
`frozen_spec._read_frozen_inputs`.

`syntax.formula` uses fixed constructor classes and exact canonical object
shapes. `syntax.parser` and `syntax.pretty` use fixed notation tables, not YAML
lookups, and do not participate in serialized certificate acceptance.
`kernel.document` implements the fixed certified JSON document profile rather
than dynamically interpreting its YAML strings. The entire document-boundary
object, all other contract fields, and the complete source file remain locked.
There is no runtime read of Markdown, the source register, obligations, a
legacy rule registry, or an external manifest.

## Constructor coverage

This table describes the existing frozen declaration; tests mutate only copies.
The atom `name` field is payload, not a traversable formula child.

| Constructor | Arity | Declared fields | Primitive | Definition link |
| --- | ---: | --- | --- | --- |
| atom | 0 | name | true | absent |
| neg | 1 | arg | true | absent |
| and | 2 | left, right | true | absent |
| poss | 1 | arg | true | absent |
| or | 2 | left, right | false | DEF_OR |
| strict_imp | 2 | left, right | false | DEF_STRICT_IMP |
| equiv_s | 2 | left, right | false | DEF_EQUIV_S |

Every declaration is now covered in full: field presence, list order, arity,
classification, object level, surface status, definition association, added or
removed fields/operators, and any future field inside the pinned file. The
manifest records only file paths, Git identities, and digests; no declaration
above is copied into a new executable registry.

## Effect of the audited defect

Confirmed before repair on the exact replay: changing only
`language.formula_ast.and.fields` to `[left]` allowed `_match` to skip the
second implication in `DEF_EQUIV_S.rhs`. A B5 instance `p ⥽ ∼∼p`, adjoined
to itself, was falsely accepted as sufficient evidence for contraction to
`p ≡ₛ ∼∼p`. The defect is acceptance of an invalid derivation: its required
reverse implication was never matched. The same change falsely matched B1
against `(p ∧ q) ⥽ (q ∧ r)` by skipping both right children. Existing AST
and contract locks were unchanged in both reproductions.

`_instantiate` reads the same unchecked field lists. Missing/renamed fields
can cause constructor failures; such failures are not claimed as an observed
false acceptance. They now reject at initialization as well. Schema-driven
postulate checking and explicit conversion are therefore guarded at their
common input boundary.

Occurrence resolution/rebuilding, Sa substitution and atom collection, and
Sb's direct replacement use `contract.occurrence_path.traversable_fields`.
That object was already locked, so changing `language.formula_ast` alone does
not redirect these traversals. Sb can nevertheless consume an equivalence
falsely admitted by the conversion defect. Regression coverage includes that
downstream use, every direct traversal path, the previously locked contract
declarations, and the schema/definition calls used to establish parents.
Ad/Smp have fixed operations, with formula validation using the same locked
occurrence table; they can also consume falsely established ancestors.
Diagnostic erasure reads definition associations but is never used to rescue
a failed rule. Those associations now receive complete-file integrity too.

## Repair boundary

The checker-owned `kernel/frozen_baseline.py` manifest derives from pure
administrative freeze `33e6a14a4b92534ea159868060576d1b45da9bb5`, whose parent
is certified candidate `21117f3da827f873c3ed88b578a1681aabfca7ac`.
The loader reads each of six files once into bytes, parses those same bytes
using its existing unique-key YAML loader, retains existing metadata/semantic
diagnostics, and validates all six raw digests. Only then does it construct
`FrozenBasis`, recursively immutable mappings, and `FrozenSpec`. Preflight
basis validation constructs no trusted models. No theorem checking or trusted
transform runs during preflight. A byte-different file, even a comment-only
edit, is outside this exact frozen baseline. Copying the ordinary files works
without Git or `audit/m1`; a caller-supplied manifest cannot authorize edits.

The separate certificate JSON decoder is unchanged. Manifest changes are
checker changes requiring review, not an option for a temporary spec to supply
alternative semantics. Independent M1 re-audit remains required.
