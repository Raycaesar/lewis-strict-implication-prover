M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED

# Work Max — focused closure recheck of the M0.3 foundational repair

**Repository:** `Raycaesar/lewis-strict-implication-prover`  
**Immutable candidate audited:** `5339a5a4f4c56a5e4feae3cc452730e488a309f1`  
**Candidate tree:** `327b56bf8eb08be1665274da09d5c0e99bc5357e`  
**Direct predecessor:** `4931e4daa124587a789ac27b841f499295facf5e`  
**Commit subject:** `repair M0 trusted certificate boundary for closure audit`  
**Commit timestamp:** 2026-09-05 01:35:25 +08:00 / 2026-09-04 17:35:25 UTC  
**Audit date:** 2026-09-04 UTC  
**Mode:** read-only closure recheck; this report is not part of the audited tree.

> **Candidate-identification note.** The supplied prompt names the predecessor SHA but does not literally print a second, M0.3 SHA. The repository contained exactly one subsequent commit, it is the direct child of the predecessor, and its subject identifies it as the M0 trusted-certificate-boundary repair. I therefore detached the audit worktree at the full SHA above. This verdict applies only to that object, not to any later state of `main`. If another SHA was intended, this report does not audit it.

## 1. Overall verdict

Commit `5339a5a4f4c56a5e4feae3cc452730e488a309f1` is **not yet safe to freeze as the immutable M0 logical basis for M1**.

The repair is substantial and largely correct. The predecessor's P0 concerning visible use of 11.01–11.03 is closed: M0.3 chooses explicit, one-occurrence `definition_conversion`, prohibits implicit elaboration in all Lewis operations, uses exact surface-AST matching, and makes conversion a metalinguistic certificate check rather than a fifth Lewis rule. The requested separation of parentless schema instantiation from one-parent object-level `Sa` is also mathematically clear, and the shared occurrence-path grammar is deterministic.

The formula and system layer has not regressed. Parsed-object comparison against the predecessor establishes byte-independent AST equality for B1–B8, A8, C10–C12 and all three definition AST pairs; displays are unchanged; all normalized basis memberships are unchanged; and every stored fingerprint matches both states.

Certification nevertheless fails for two P1 specification defects and associated P2 closure defects:

1. the logical certificate serialization is not closed under fields: proof nodes reject extra fields, but justification objects do not. The contracts enumerate required fields and a selected forbidden vocabulary without saying that all other fields are rejected. Node/reference scalar types are also not fixed. Two conforming-looking kernels can therefore accept different certificate documents;
2. the S5 bridge entries use `source_basis_id` and `target_basis_id` in the opposite direction from the normative rule that bridge expansions check in the **target** basis. Following the prose makes the stored pairs wrong; following the stored pairs gives the fields a different meaning. This is exactly the kind of cross-basis ambiguity the repair was meant to remove.

In addition, the claimed Parry provenance repair is incomplete: two active entries retain the expressly rejected “all 11.1–11.7 as postulates” claim and two others retain ambiguous unreduced-list shorthand. The `--freeze` validator also accepts mutations that negate central repaired invariants. Green CI therefore establishes repository consistency only under the checks actually encoded; it does not close the audit defects.

**M1 trusted-kernel implementation may not begin from this commit.** The remaining repair is narrow and does not require replacing a definition AST, schema AST, or normalized S1–S5 basis.

## 2. Executive closure matrix

| Closure question | Result | Finding |
| --- | --- | --- |
| A. Definition conversion | **Closed** | One explicit surface occurrence, one definition, one direction, one metavariable environment, exact conclusion; no implicit conversion and no circularity with `Sb`. |
| B. `postulate_instance` versus `Sa` | **Substantively closed; serialization gap remains** | Namespace, parent count, map domains, simultaneity and rendering are clear. Unknown justification fields and ID/reference types remain unspecified (P1-01). |
| C. Occurrence paths | **Closed** | One list-valued grammar, root `[]`, formula-valued `arg/left/right`, atom rejection, surface traversal, one occurrence. |
| D. S5 basis identity | **Basis closure passes; bridge closure fails** | The two S5 bases are separate and anti-union. The recorded bridge direction conflicts with the normative target-basis expansion rule (P1-02). |
| E. Formula/system non-regression | **Pass** | All 15 audited AST objects and all six resolved bases, counting the alternative S5 basis separately, equal the predecessor. |
| F. Source/provenance | **Partial fail** | The p. 498 qualification and p. 501 basis source are repaired. Two active Parry statements still expressly say that Parry uses all 11.1–11.7 as postulates, and two shorthand entries remain ambiguous (P2-01). |
| G. Validators and CI | **Partial fail** | All gates and 35 tests pass in a declared-dependency environment; exact-SHA CI is green and Zone files are absent. Targeted semantic mutations nevertheless pass `--freeze` (P2-02). |

### Defect totals

| Severity | Count | Freeze effect |
| --- | ---: | --- |
| P0 | 0 | The predecessor's sole P0 is closed. |
| P1 | 2 | Certification and M1 start are blocked. |
| P2 | 4 | Provenance and freeze-integrity closure is incomplete. |
| P3 | 2 | Optional hardening; not independent certification blockers. |

## 3. Audit scope and immutable-state controls

The candidate was checked out as a detached worktree at the full SHA above. Local `HEAD`, the candidate tree, the direct-parent relation, and the GitHub Actions run all agree on the candidate identity. The source worktree was clean before this report was created. `git ls-files '*:Zone.Identifier'` returned no path.

The required files were read in the order given in the prompt. I additionally inspected the active source policy, specification README, freeze checklist, roadmap, test fixture and relevant historical-snapshot notices because they bear directly on claims of closure.

The complete `Strict_Implication/` tree is unchanged from the predecessor. For the only disputed provenance point, I directly re-inspected Parry 1939 pp. 137–138 and L&L pp. 498 and 501. A second formula-by-formula historical audit was neither necessary nor used as a shortcut: formula identity was checked mechanically against the already source-audited predecessor.

## 4. A — P0 closure: definition conversion

### 4.1 Frozen status of the three definitions

M0.3 consistently treats the following as registered metalinguistic definitions over first-class surface nodes:

| Definition | Surface form | One-step expansion | Result |
| --- | --- | --- | --- |
| `DEF_OR` / 11.01 | `or(P,Q)` | `neg(and(neg(P),neg(Q)))` | Pass |
| `DEF_STRICT_IMP` / 11.02 | `strict_imp(P,Q)` | `neg(poss(and(P,neg(Q))))` | Pass |
| `DEF_EQUIV_S` / 11.03 | `equiv_s(P,Q)` | `and(strict_imp(P,Q),strict_imp(Q,P))` | Pass |

`spec/language.yaml:219–239`, `spec/rules.yaml:223–252,285–318`, `docs/FOUNDATIONAL_SPEC_v0.3.md:61–88`, and `docs/PROOF_CERTIFICATE_SPEC.md:397–516` now agree on the controlling policy:

- no Lewis primitive operation expands or contracts a definition implicitly;
- `Sa`, `Sb`, `Ad`, and `Smp` match exact visible ASTs;
- a visible definition change is a separate `definition_conversion` node;
- full erasure into `atom/neg/and/poss` is diagnostic and is not a fallback equality relation for proof checking.

### 4.2 Deterministic conversion algorithm

The normative conversion payload uses exactly one parent, a registered `definition_id`, one of `expand|contract`, and one occurrence path. The checker is required to:

1. resolve the definition;
2. traverse the parent's surface AST at the recorded path;
3. match the selected subformula against the direction's source pattern;
4. construct one consistent metavariable environment, enforcing structural equality at repeated metavariables;
5. instantiate the opposite side with that same environment;
6. replace the selected tree occurrence only;
7. require exact structural equality with the declared conclusion.

For this binder-free first-order formula grammar, the selected path and directional pattern make the match deterministic. There is no license for associative, commutative, erasure-based, or multi-step matching.

### 4.3 Classification and `Sb` interaction

The project correctly classifies conversion as trusted checking of notation, not a fifth Lewis inference operation. The four-operation historical list remains unchanged.

There is no circularity with `Sb`. If a proof has `A ⥽ B` and `B ⥽ A`, it must first use `Ad`, then explicitly contract the resulting conjunction via `DEF_EQUIV_S`, and only then use the exact surface `equiv_s(A,B)` formula as the first parent of `Sb`. Definition contraction neither invokes `Sb` nor assumes an object-level equivalence not already represented by its registered defining form.

### 4.4 P0 determination

**P0-01 from the predecessor audit is closed.** No new P0 was found.

The first-class `equiv_s` normalization is now sufficiently faithful and proof-theoretically controlled for a trusted syntactic checker, subject to the remaining general certificate-serialization P1 below.

## 5. B — postulate instances versus `Sa`

| Property | `postulate_instance` | `Sa` | Result |
| --- | --- | --- | --- |
| Parents | none | exactly one already accepted theorem | Pass |
| Key namespace | schema metavariables represented by `{meta: ...}` | object atom names in the parent | Pass |
| Domain | exactly all and only metavariables occurring in the selected schema | nonempty subset of parent atom names; extra/nonoccurring keys rejected | Pass |
| Values | object formulas with no schema metavariable nodes | object formulas with no schema metavariable nodes | Pass |
| Application | one simultaneous schema instantiation | simultaneous, one-pass, nonrecursive; unmentioned atoms fixed | Pass |
| Basis check | `schema_id` must be primitive in exact `basis_id` | inherited from the accepted parent theorem | Pass |
| Implicit definitions | none | none | Pass |
| Rendering | rendered as schema label, never cosmetically as `Sa` | rendered as actual `Sa` only | Pass |

The namespace distinction is structural, not merely typographical: schema metavariables are `{meta: P}` nodes in registered schemas, whereas proof formulas contain only object ASTs such as `{op: atom, name: ...}`. Thus even an object atom whose string happens to be uppercase remains an object atom by node kind.

The mathematical distinction required by the predecessor P1-01 is closed. The remaining P1-01 in this report is a serialization-closure defect common to all justification kinds, not a renewed conflation of these operations.

## 6. C — normative occurrence paths

The single grammar is stated in both `spec/rules.yaml:290–318` and `docs/PROOF_CERTIFICATE_SPEC.md:230–288` and is shared by `Sb` and `definition_conversion`.

| Case | Normative result |
| --- | --- |
| Root | `[]` selects the whole surface formula. |
| Unary child | `[arg]` is valid only at `neg` or `poss`. |
| Binary child | `[left]` and `[right]` are valid at `and`, `or`, `strict_imp`, or `equiv_s`. |
| Nested child | Lists such as `[right, arg]` traverse one child at each segment. |
| Atom | No further path is valid; `name` is data and is never traversable. |
| Defined node | Traversed as the visible binary surface node; no expansion occurs. |
| Dotted path | renderer-only and rejected as a logical payload. |
| Replacement cardinality | exactly the single occurrence selected by the path; further changes require further nodes. |

This is sufficient for independent implementations to agree on occurrence selection. The path layer itself is closed.

## 7. D — S5 basis identity and bridge architecture

### 7.1 Primitive basis admission

Every proof must declare one allowed `(system,basis_id)` pair. Resolution gives:

| Basis ID | Exact primitive schemas | Result |
| --- | --- | --- |
| `S1_B1_B7` | B1–B7 | Pass |
| `S2_B1_B8` | B1–B8 | Pass |
| `S3_B1_B7_A8` | B1–B7+A8 | Pass |
| `S4_B1_B7_C10` | B1–B7+C10 | Pass |
| `S5_PRIMARY_B1_B7_C11` | B1–B7+C11; C10/C12 not primitive | Pass |
| `S5_ALT_B1_B7_C10_C12` | B1–B7+C10+C12; C11 not primitive | Pass |

No union basis is declared. `postulate_instance` admission is expressly basis-specific. The original P1-03 concerning primitive S5 basis selection is closed.

### 7.2 Bridge direction is internally inconsistent

The normative prose says that a bridge carries `source_basis_id` and `target_basis_id` and must expand to a native certificate valid in the **target basis** (`docs/PROOF_CERTIFICATE_SPEC.md:558–565`; `docs/ARCHITECTURE.md:152–159`; repair log lines 166–173).

Under that meaning, a bridge translating a proof from basis X into basis Y must prove every X-only primitive used by the expansion under Y. The two stored entries are reversed:

| Obligation | Native derivation actually required | Correct translation direction under the normative prose | Stored pair in `spec/systems.yaml` |
| --- | --- | --- | --- |
| `C10_C12_DERIVE_C11` | prove C11 under the alternative C10+C12 basis | primary → alternative | alternative → primary |
| `C11_DERIVES_C10_C12` | prove C10 and C12 under the primary C11 basis | alternative → primary | primary → alternative |

Following the stored `target_basis_id` makes each required expansion trivial in the wrong way: C11 is already primitive in the recorded primary target, and C10/C12 are already primitive in the recorded alternative target. It therefore fails to certify cross-basis import.

The opposite reading—`source_basis_id` means the basis in which the displayed derivation is carried out and `target_basis_id` means the basis whose extra axioms are thereby recovered—makes the stored pairs intelligible, but contradicts the explicit rule that the expansion checks in the target basis. Two implementers can reasonably choose opposite readings and still point to M0.3 text. This is P1-02.

The repair should either swap the two pairs under the existing translation semantics or replace the ambiguous names with fields such as `from_basis_id` and `into_basis_id`, declaring that the expanded certificate's own `basis_id` must equal `into_basis_id`. The theorem statements themselves are correct and require no calculus change.

## 8. E — formula and system non-regression

### 8.1 Direct predecessor comparison

The following comparisons were performed on parsed YAML objects from the two Git objects, not on formatting or line-oriented diffs:

| Locked layer | Objects compared | Result |
| --- | ---: | --- |
| Primitive schema ASTs | B1–B8, A8, C10, C11, C12 (12) | all equal |
| Metadefinition AST pairs | `DEF_OR`, `DEF_STRICT_IMP`, `DEF_EQUIV_S` (3) | all equal |
| Schema display strings | 12 | all equal |
| Definition display strings | 3 | all equal |
| Normalized primary bases | S1–S5 | all resolved sets equal |
| Alternative S5 basis | one | resolved set equal |
| Historical source corpus | complete `Strict_Implication/` tree | no Git diff |

Consequently the previous source audit's positive results for every connective, negation, and grouping remain applicable. No new formula-level historical claim was introduced by an AST change.

### 8.2 Fingerprint mechanism

`audit/m0/certified_ast_fingerprints.yaml` stores SHA-256 values over canonical JSON encodings of the twelve schema ASTs and the `{lhs,rhs}` pair of each definition. All fifteen current hashes match. Independently computing the same hashes from predecessor commit `4931e4d…` also matches every lock entry.

This is useful protection against accidental formula drift, including a visually elusive C10 negation change. It does **not** prove historical accuracy; that authority comes from the predecessor's direct source audit. It also does not lock display strings, system memberships, rule semantics, or certificate grammar. Finally, `validate_spec.py` does not validate `lock_version` or `basis_commit_audited`, and a deliberate simultaneous edit of an AST and its lock file would pass. Those are limitations of a regression tripwire, not reasons to reject the unchanged formula layer.

## 9. F — source and provenance closure

### 9.1 Parry 1939

Direct inspection of p. 137 shows the displayed S3 postulate list to be 11.1, 11.2, 11.3, 11.4, 11.6, 11.7, and 30.1/A8. It does not display 11.5. Page 138 credits McKinsey with deriving 11.5 from the remaining material and then uses the full 11.1–11.7 theorem stock.

The repaired explanatory passages in `docs/FOUNDATIONAL_SPEC_v0.3.md:192–195`, `docs/SOURCE_POLICY.md:114–122`, `spec/systems.yaml:73–76`, and `audit/m0/source_register.yaml:20–23,304–311` state this accurately.

However, two active passages still make the expressly rejected literal claim that Parry directly or explicitly uses all 11.1–11.7 together with 30.1 **as postulates**:

- `spec/systems.yaml:12–13`;
- `spec/schemas.yaml:20–21`.

Two further entries use shorthand that is mathematically defensible as a claim of deductive support but remains needlessly ambiguous about Parry's displayed basis:

- `spec/schemas.yaml:296–297`;
- `audit/m0/source_register.yaml:231`.

The first two passages conflict with the corrected text in the same candidate and with the source. The latter two can be read as saying only that Parry supports the unreduced presentation, but they should adopt the project's already-frozen reduced-list wording rather than leave the prohibited reading available. The issue is not the mathematical safety of the unreduced `B1–B7+A8` basis, which remains established. It is a failure to complete the exact provenance repair claimed by the repair log and checked off at `audit/m0/FREEZE_CHECKLIST.md:22`.

### 9.2 L&L pp. 498 and 501

The p. 498 qualification is now preserved: items (12)–(14) are explicitly recorded under that paragraph's A1–A8/B1–B9 background. The register does not misrepresent those statements as machine certificates.

Page 501 is now used as the canonical direct source for the two B1–B7-based S5 presentations. This is correct and is repeated consistently in the active foundational spec, system spec and source register.

Thus the L&L provenance repair passes; the Parry repair is incomplete.

## 10. G — validators, rejection tests and CI

### 10.1 Executed results

| Command/check | Result |
| --- | --- |
| `python scripts/validate_spec.py` | Pass; 7 constructors, 12 schemas, 4 Lewis rules, 6 trusted certificate kinds, 5 systems |
| `python scripts/validate_source_register.py` | Pass |
| `python scripts/validate_spec.py --freeze` | Pass |
| `python scripts/validate_source_register.py --freeze` | Pass |
| bare `pytest` in the base runtime | executable absent; environment condition, not a repository defect |
| declared-dependency environment, `python -m pytest` | **35 passed in 0.57 s** |
| tracked `*:Zone.Identifier` | none |
| exact-SHA GitHub Actions | [run 33901398537](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/33901398537) completed successfully; every listed step passed |

CI coverage now includes `AGENTS.md`, README/CONTRIBUTING, `docs/**`, `spec/**`, `audit/m0/**`, scripts, tests, `pyproject.toml`, and the workflow. It also rejects tracked Zone metadata and runs both validator modes. These predecessor P2 repairs pass.

### 10.2 What the strengthened tests genuinely establish

The suite contains useful negative mutations. It rejects an extra AST constructor, a recursive definition, definition metavariable-set drift, a malformed path-segment registry, removal of the conversion kind, a high-risk C10 AST mutation through the fingerprint, an S5 basis-ID collision, duplicate YAML keys, and missing spec files.

This is materially stronger than the predecessor suite. It is still not a certificate checker, nor should M0 silently become M1. The problem is narrower: the freeze validator does not lock many of the normative data fields that M0.3 itself makes authoritative.

### 10.3 Demonstrated freeze-gate false positives

I applied each of the following mutations in memory and ran `validate_bundle(..., freeze=True)`. Every mutation was accepted with zero issue:

| Mutation accepted by `--freeze` | Frozen invariant contradicted |
| --- | --- |
| Change postulate map domain to allow missing keys | exact schema-metavariable domain |
| Replace the one-environment conversion check by independent environments | deterministic definition matching |
| Replace the no-second-conversion check by arbitrary further conversions | explicit one-step definition conversion |
| Change `Sb` to permit any number of replacements | exact one-occurrence replacement |
| Say that `atom.name` is traversable | normative path rejection |
| Swap an S5 bridge basis pair | bridge orientation/identity |
| Add a policy saying unknown justification fields are ignored | closed trusted serialization |

The reason is visible in `scripts/validate_spec.py:363–424`: it checks selected names, parent counts, required-field sets, the three path-segment names, selected namespace strings and a few flags, but not the full forbidden-field sets, conversion checks, `Sb` replacement constraint, path traversal/rejection contract, bridge metadata, or closed justification objects.

The source validator likewise verifies the corrected text only in `secondary_sources.PARRY1939.use`; it does not inspect the contradictory active Parry claims listed in Section 9. Its PASS is therefore a false negative for the very provenance repair it claims to gate.

### 10.4 Freeze-state transition limitation

`validate_source_register.py:204–211` requires the six original P0/P1 repairs to remain exactly `repair_implemented_reaudit_pending` in freeze mode, even though `closed` is declared closure-ready and `frozen_source_audit` is accepted at the register level. A later truthful transition of these obligations to `closed` would therefore make `--freeze` fail. This does not alter the current calculus, but the gate should distinguish closure-candidate mode from post-certification frozen mode.

### 10.5 CI interpretation

The exact-SHA green run proves that the repository passes its encoded checks under Python 3.12 and has no tracked Zone files. It does not prove the missed provenance, bridge-direction, or serialization invariants. CI success is therefore positive evidence of reproducibility, not a mathematical or specification certification.

## 11. Full P0–P3 defect register

### P0

**None.** The predecessor's definition-conversion blocker is closed.

### P1-01 — justification objects and reference identifiers do not have a closed serialization

1. **Locations:** `spec/rules.yaml:18–40,64–84,110–126,150–166,180–252,319–327`; `docs/PROOF_CERTIFICATE_SPEC.md:30–41,83–129,133–226,292–407`.
2. **Exact defect:** proof-node objects explicitly reject extra node fields, but no parallel rule says that each `justification` object has exactly its declared fields. `required_fields` plus a finite `forbidden_fields` list leaves arbitrary keys unspecified. Top-level fields are described as exactly the “logical” fields without defining whether annotations are allowed, and node IDs/root/parent references have no normative scalar type or equality convention.
3. **Why it matters:** one kernel may reject an unknown justification key while another ignores or interprets it. Integer versus string node IDs can likewise be accepted differently. Both can claim to implement the present prose. This violates the prompt's independent-implementation certificate-set criterion.
4. **Required repair:** make every logical object closed-world. Give an exact allowed-field set per justification kind; reject every other key; either forbid annotations or isolate them in a precisely declared ignored metadata object. Specify nonempty-string node IDs, string parent/root references, strict duplicate-key rejection, and exact string identity.
5. **Changes intended calculus?** No. This changes only serialization determinacy.
6. **Re-audit dependency:** contract prose, `rules.yaml`, validator checks, and rejection mutations for an arbitrary extra key, wrong scalar types, duplicate IDs/keys, and mixed string/integer references.

### P1-02 — S5 bridge source/target basis semantics conflict with the stored bridge pairs

1. **Locations:** `spec/systems.yaml:138–153,163–164,196–198`; `docs/PROOF_CERTIFICATE_SPEC.md:558–565`; `docs/ARCHITECTURE.md:152–159`; `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.3.md:166–173`.
2. **Exact defect:** the prose requires bridge expansion under `target_basis_id`, while both stored source/target pairs designate as target the basis whose characteristic axiom is being derived rather than the basis in which that derivation must check.
3. **Why it matters:** the recorded target makes the bridge proof primitive/trivial and does not justify cross-basis import. Alternatively interpreting the fields to rescue the data contradicts the normative prose. Independent M1/M5 implementations can reverse the translation.
4. **Required repair:** define the fields operationally and consistently. Under the existing “expand in target” policy, use primary→alternative for the C11-under-C10+C12 bridge and alternative→primary for the C10/C12-under-C11 bridge. Require the expanded certificate's `basis_id` to equal the declared target/into basis. Add wrong-direction and primitive-trivialization rejection tests.
5. **Changes intended calculus?** No. The two bases and three historical derivability claims stay unchanged.
6. **Re-audit dependency:** system bridge entries, bridge contract prose and bridge-direction validator/tests only; no formula/source re-audit.

### P2-01 — Parry provenance correction is incomplete

1. **Locations:** `spec/systems.yaml:12–13`; `spec/schemas.yaml:20–21,296–297`; `audit/m0/source_register.yaml:231`; contradicted by the accurate passages cited in Section 9.
2. **Defect:** the first two active passages still say Parry uses all 11.1–11.7 plus 30.1 as the postulates he takes for S3, whereas his displayed list omits 11.5 and recovers it by McKinsey's theorem. The other two use ambiguous full-list shorthand instead of the project's own exact qualification.
3. **Required repair:** replace all four with the already-correct reduced-list/derived-11.5 wording; keep the conclusion that unreduced B1–B7+A8 is a safe normalized basis.
4. **Freeze effect:** the calculus is unchanged, but exact source-faithful closure and the checklist's provenance claim are presently false.

### P2-02 — freeze validation does not protect the repaired certificate invariants

1. **Locations:** `scripts/validate_spec.py:363–424,485–529,538–569`; `scripts/validate_source_register.py:167–180,204–211`; `tests/spec/test_rule_spec.py`, `test_source_register.py`, and `test_system_spec.py`.
2. **Defect:** the seven directly tested counter-mutations in Section 10.3 all pass `--freeze`. The source validator checks one correct Parry summary but not contradictory executable provenance. Bridge direction is unvalidated.
3. **Required repair:** structurally validate every normative contract component, not just selected strings; add rejection mutations for all seven cases; make source checks cover all active provenance fields.
4. **Freeze effect:** this is a P2 rather than a mathematical P1 because the exact candidate can still be human-audited, but the advertised freeze gate does not reliably prevent foundational drift.

### P2-03 — repair log uses a nonnormative singular parent field

1. **Locations:** `audit/m0/M0_FOUNDATIONAL_REPAIR_LOG_v0.3.md:46–53`, versus `spec/rules.yaml:227–240` and `docs/PROOF_CERTIFICATE_SPEC.md:399–409`.
2. **Defect:** the log's code block says `parent`; the adopted unified serialization uses the one-element list `parents`.
3. **Required repair:** change the log to `parents: [<node-id>]` or label `parent` as conceptual prose rather than a payload field.
4. **Freeze effect:** the normative hierarchy makes this documentary rather than P1, but it should not remain in a closure record.

### P2-04 — fingerprint provenance metadata is not validated

1. **Locations:** `audit/m0/certified_ast_fingerprints.yaml:1–4`; `scripts/validate_spec.py:538–558`.
2. **Defect:** hashes are checked, but `lock_version` and `basis_commit_audited` are ignored; changing an AST and its lock together also passes.
3. **Required repair:** freeze the lock schema and audited predecessor SHA, and document that changing either AST or locked hash is an explicit re-audit event. The validator cannot replace review of a deliberate lock update.
4. **Freeze effect:** current hashes are independently verified and correct; this is protection/hygiene, not a defect in the current formulas.

### P3-01 — use operational bridge field names

Prefer `from_basis_id` / `into_basis_id` (or `certificate_basis_id`) over bare source/target names. This would make the required checking environment visible at the data level.

### P3-02 — provide a small normative certificate-schema fixture at M1 start

Once M1 begins after certification, add one valid and one minimally invalid certificate for each justification kind. These should test the frozen M0 contract without changing it. This is not required to settle the present mathematical basis.

## 12. Exact closure checklist status

| Item | Status |
| --- | --- |
| Candidate detached at full SHA and tree recorded | Pass |
| Candidate is direct child of audited predecessor | Pass |
| 11.01–11.03 ASTs unchanged | Pass |
| B1–B8, A8, C10–C12 ASTs unchanged | Pass |
| Normalized S1–S5 memberships unchanged | Pass |
| Fingerprints match predecessor and candidate | Pass |
| Explicit `definition_conversion` normative | Pass |
| No implicit conversion in Lewis rules | Pass |
| Exact surface-AST matching | Pass |
| One definition, direction, parent and occurrence per conversion | Pass |
| One consistent conversion metavariable environment | Pass |
| `definition_conversion` not a fifth Lewis rule | Pass |
| `equiv_s`/`Sb` interaction noncircular | Pass |
| `postulate_instance` parentless with exact schema map | Pass |
| `Sa` one-parent object-atom substitution | Pass |
| `Sa` simultaneous, one-pass, nonrecursive | Pass |
| Renderer distinguishes direct schema instances from `Sa` | Pass |
| One shared path grammar with atom rejection | Pass |
| Every proof requires a stable `basis_id` | Pass |
| S5 primary admits C11 only as its extension | Pass |
| S5 alternative admits C10+C12 only as its extensions | Pass |
| No S5 union basis | Pass |
| Future bridge direction unambiguous and correct | **Fail — P1-02** |
| Logical justification serialization closed | **Fail — P1-01** |
| Parry provenance accurate in every active field | **Fail — P2-01** |
| p. 498 qualification preserved | Pass |
| p. 501 is canonical source for direct S5 bases | Pass |
| normal and freeze validators pass | Pass as executed |
| 35 tests pass under declared dependencies | Pass |
| validator rejects semantic repair regressions | **Fail — P2-02** |
| CI covers governing files and passes exact SHA | Pass |
| tracked Zone metadata absent | Pass |
| no P0 remains | Pass |
| no P1 remains | **Fail** |
| candidate safe for M1 | **Fail** |

## 13. Minimal repair plan

1. Close the justification grammar and node/reference scalar types. Add exact allowed-field sets and unknown-field rejection.
2. Resolve bridge direction. Under the current target-basis-checking semantics, swap both S5 bridge pairs and require expansion certificate `basis_id == target_basis_id`; alternatively rename and redefine the fields consistently.
3. Replace the two inaccurate and two ambiguous Parry statements with the reduced-list/11.5-derivation wording already present elsewhere.
4. Correct the repair log's singular `parent` payload example.
5. Strengthen `--freeze` and its mutation suite so the seven demonstrated counter-mutations fail; validate bridge orientation and all active Parry claims; validate fingerprint-lock metadata.
6. Re-run the four validator commands, the full test suite, Zone check and exact-SHA CI on a new commit.
7. Perform a narrow closure recheck of these repaired locations. Do not re-audit B1–B8, A8, C10–C12 or 11.01–11.03 unless a locked AST changes.

No Box, B9, A1–A7 executable duplication, new Lewis rule, semantic proof rule, or M1 implementation is needed for this repair.

## 14. Final recommendation

The M0.3 repair validates the project's substantive logical direction. The native formula layer, the normalized S1–S5 bases, the explicit conservative definition-conversion design, `postulate_instance`/`Sa` separation, and occurrence-path semantics are all fit to retain unchanged.

However, commit `5339a5a4f4c56a5e4feae3cc452730e488a309f1` must not be tagged or treated as the immutable M0 foundation. The remaining P1 defects can cause independent implementations to disagree about accepted certificate documents and cross-basis expansion. The unresolved provenance and freeze-gate P2 defects also make the candidate's own closure claims inaccurate.

**M1 trusted-kernel implementation may not begin.** After the minimal repair plan is committed and a focused exact-SHA recheck finds no P0/P1 or freeze-undermining P2 defect, M0 may be certified without changing the audited formula/system layer.
