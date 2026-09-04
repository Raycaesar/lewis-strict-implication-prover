M0 FOUNDATIONAL SPECIFICATION NOT CERTIFIED

# From-scratch M0 foundational audit of the Lewis S1-S5 native syntactic prover

**Repository:** `Raycaesar/lewis-strict-implication-prover`  
**Immutable audit candidate:** `4931e4daa124587a789ac27b841f499295facf5e`  
**Candidate tree:** `922ee26637c782996a04962e11be237060f6c7b1`  
**Commit subject:** `add M0 foundational source audit infrastructure`  
**Audit date:** 2026-09-04 (UTC)  
**Audit mode:** read-only with respect to the candidate; this report is the only output and is not part of the audited tree.

## 1. Overall verdict

The exact repository state at commit `4931e4daa124587a789ac27b841f499295facf5e` is **not certifiable as an immutable M0 foundation**.

The negative verdict is not caused by a bad Lewis axiom, a wrong S1-S5 basis, the absence of Box, the exclusion of B9, or the normalized use of `equiv_s`. Direct comparison with Lewis and Langford finds the executable definitions and all twelve stored schema ASTs correct. The four primitive operations are also correctly identified, and Parry supplies adequate syntactic support for the normalized S3 basis `S1 + A8`.

Certification fails because the candidate deliberately leaves freeze-critical trusted-kernel semantics unresolved. In particular:

1. `spec/language.yaml` says that the kernel *may* elaborate definitions, while `spec/rules.yaml` treats expansion and contraction as parser/renderer normalization and `docs/PROOF_CERTIFICATE_SPEC.md` offers, but does not adopt, an explicit `definition_conversion` certificate node.
2. The certificate contract does not uniquely distinguish axiom-schema instantiation from Lewis substitution (`Sa`), and its node names and payload field names disagree across the executable and prose specifications.
3. The structural occurrence-path language needed by `Sb` and definition conversion is not defined.
4. A certificate identifies only `system: S5`, although `spec/systems.yaml` contains two distinct S5 primitive bases. The checker is not told which basis governs primitive-schema admission.

These are genuine trusted-boundary ambiguities: two reasonable M1 implementations could accept different certificates while both claiming conformance to this commit. M1 therefore may not begin from this state.

There is, however, no need to redesign the intended calculus. The principal repair is to freeze one precise conservative definitional-extension and certificate contract. No stored schema AST or normalized system basis needs mathematical replacement on the evidence examined.

## 2. Executive summary

### 2.1 Audit result by area

| Area | Result | Finding |
| --- | --- | --- |
| Immutable candidate identity | Pass | Detached checkout and GitHub metadata agree on the requested SHA and tree. |
| L&L definitions 11.01-11.03 | Formula transcription pass; policy fail | All three expansions are correct, but the kernel status of the first-class defined nodes is not frozen. |
| Primitive operations | Pass at the logical/source level | `Sa`, `Sb`, `Ad`, and `Smp` correctly correspond to L&L Substitution (b), Substitution (a), Adjunction, and Inference. |
| B1-B8, A8, C10-C12 | Pass | Display strings and YAML ASTs match the canonical pages, including every high-risk modal negation. |
| A-series normalization | Pass, with provenance clarification required | A1, A3, A5, A6 are literal matches; A2, A4, A7 are S1 consequences. Parry supports the normalized S3 basis. |
| S1-S5 bases | Pass | The five normalized bases and the alternative S5 basis match L&L pp. 500-501. |
| C10/C11/C12 bridge plan | Pass as a historical obligation, not as a certificate | L&L states the three derivabilities, but p. 498 has an explicit background-basis qualification that the register should preserve. Native bridge certificates remain required. |
| Definition conversion | Fail, P0 | The proposed approach is sound in principle, but this commit does not make it normative or deterministic. |
| Certificate semantics | Fail, P1 | Node vocabulary, schema instantiation, `Sa`, occurrence paths, and S5 basis selection are not fixed. |
| Local validators/tests | Structural pass only | Both validators pass; 30 tests pass in an isolated environment. They do not establish historical or mathematical correctness. |
| Exact-commit CI | Pass | GitHub Actions run `33893929003` completed successfully for the audited SHA. |
| Repository freeze hygiene | Fail, P2 | Eight tracked `*:Zone.Identifier` files remain, contrary to the freeze checklist. |

### 2.2 Defect totals

| Severity | Count | Effect |
| --- | ---: | --- |
| P0 | 1 | M0 cannot be frozen. |
| P1 | 3 | Certificate/kernel specification must be repaired before M1. |
| P2 | 5 | Provenance, audit-register, CI, validation, and repository-hygiene repairs are required for a clean freeze. |
| P3 | 2 | Optional clarity and usability improvements. |

### 2.3 Positive findings that should be preserved

- Keep `neg`, `and`, and `poss` as the primitive connective constructors and keep `strict_imp`, `or`, and `equiv_s` as first-class surface nodes with registered definitions.
- Keep object-language `equiv_s` distinct from metalanguage `=` and `:=`.
- Keep Box and B9 outside M0.
- Keep exactly the four Lewis operations `Sa`, `Sb`, `Ad`, and `Smp`; do not add unrestricted necessitation.
- Keep the current twelve schema ASTs unchanged.
- Keep the normalized bases `S1 = B1-B7`, `S2 = S1+B8`, `S3 = S1+A8`, `S4 = S1+C10`, and primary `S5 = S1+C11`.
- Keep the alternative S5 basis `S1+C10+C12` as a separately identified basis whose equivalence is eventually witnessed by checked bridge certificates.

## 3. Source-by-source audit

### 3.1 Repository governing documents

`AGENTS.md`, `README.md`, `docs/SOURCE_POLICY.md`, and `docs/FOUNDATIONAL_SPEC_v0.2.md` consistently state the central trust principle: search may be modern, but accepted proofs must reduce to the selected Lewis postulates and the four native operations, modulo explicitly licensed definition handling. They correctly prohibit unrestricted necessitation, semantic-validity steps, Box in M0, object-language `=`, and B9.

The governing documents also correctly distinguish theorem inclusion from primitive-basis composition. The use of `inherit_schemas_from: S1` in `spec/systems.yaml` is only a compact way to resolve a target system's own primitive schema set. It does not by itself authorize import of a theorem proved in a different basis. Rechecking every node of an S1 certificate under a target system that literally contains B1-B7 is sound; importing a theorem across a nonliteral inclusion such as S2 to normalized S3 still requires a target-basis proof or bridge.

The decisive internal inconsistency is confined to definition/certificate handling: the architecture says the kernel may “optionally” expand definitions, the rules file assigns expansion and contraction to elaboration/rendering, and the proof-certificate document leaves an explicit conversion node undecided. That inconsistency is analyzed in Sections 4 and 10.

### 3.2 Lewis and Langford, *Symbolic Logic*, 2nd ed. (1932), supplied Dover reprint

The scan `Strict_Implication/Symbolic Logic_Lewis_Langford_1959.pdf` was inspected visually at all pages required by the audit prompt.

| Printed page | Direct finding |
| ---: | --- |
| 123 | The primitive or undefined ideas are propositions, negation, logical product, possibility/self-consistency, and logical equivalence. Definition 11.01 gives `p ∨ q` as `∼(∼p ∼q)`. |
| 124 | Definition 11.02 gives the fishhook as `∼◇(p ∼q)`. Definition 11.03 relates logical equivalence to the product of the two converse strict implications. L&L expressly note that this definition does not let them dispense with primitive equivalence because equivalence is the defining relation. Postulate 11.1/B1 is present. |
| 125 | Postulates 11.2-11.7/B2-B7 and both Substitution clauses are present. Clause (a) is replacement of equivalent expressions in either direction; clause (b) is uniform substitution in an assumption or established theorem. |
| 126 | Adjunction and Inference are exactly the two-premise operations represented by `Ad` and `Smp`. L&L explicitly warn that postulate 11.7/B7 is not the metalevel operation of Inference. |
| 493 | A1-A8 and B1-B9 are displayed side by side. The page confirms both the executable formula transcriptions and the fact that A2 and A4 are not literal copies of B2 and B4. |
| 497 | C10, C11, C12, C10.1, and C13 are displayed. The project's first (strict-implication) forms of C10-C12 match exactly. C10.1 is a derived/alternative form and need not be primitive. |
| 498 | Items (12)-(14) state C11-to-C10, C11-to-C12, and C10+C12-to-C11. The paragraph introducing these items says: “When A1-8, or B1-9, are assumed”. That qualification must not disappear from provenance. |
| 499 | The continuation says C11 is exactly equivalent to C10+C12 as an additional postulate over the background sets then under discussion. |
| 500 | S1 is deduced from B1-B7; S2 from B1-B8; historical S3 from A1-A8. The page also states the relevant theorem inclusions. |
| 501 | S4 is deduced from B1-B7+C10. S5 is deduced either from B1-B7+C11 or from B1-B7+C10+C12. This page supplies the canonical support for the two S1-based S5 presentations. |

No formula-level defect was found in the project's use of these pages.

### 3.3 Parry 1939, pp. 137-138

`Strict_Implication/Parry-1939.pdf` provides the required independent syntactic cross-check.

Parry's displayed postulate list for S3 on p. 137 is, precisely, 11.1-11.4, 11.6, 11.7, and 30.1/A8. On p. 138 he cites McKinsey's derivation of 11.5 from the remaining S1 material. Thus it is mathematically harmless to describe the resulting system as `11.1-11.7 + 30.1`, but it is not literally accurate to say that Parry displays all of 11.1-11.7 as primitive postulates.

More importantly, Parry states that B1-B7 or A1-A7 determine S1, proves/records that the S1 theorems of L&L Sections 1-4 are available, derives B8/19.01 in S3, and lists the route by which the emended Survey postulates A1-A8 are obtained. This is adequate syntactic support for using `B1-B7 + A8` as the normalized executable basis of S3.

### 3.4 Feys, *Modal Logics*

`Strict_Implication/feys_modal_logic.pdf` was checked at printed pp. 43-44 and 48.

- 30.21 is uniform substitution.
- 30.22 is adjunction.
- 30.23 is detachment for strict implication.
- 30.24 is replacement of strict equivalents.
- 30.35 treats strict equivalence as the conjunction of the two converse strict implications.
- 31.022 and 31.04 visibly use “By df 30.35” to move between the conjunction and strict-equivalence notation.

Feys therefore supports both the four-rule cross-check and the proposed treatment of visible definitional changes as explicit, checked “by definition” conversions. This support does not override L&L; it shows that the conservative normalization proposed below is native to the later syntactic tradition rather than a modern semantic import.

### 3.5 McKinsey 1934

`Strict_Implication/McKinsey-1934.pdf`, pp. 425-427, repeats L&L's primitive ideas, definitions, and operations and proves 11.5 from the remaining listed material. It corroborates Parry's treatment of 11.5 as redundant in a reduced basis. The project may nevertheless retain B5 because L&L's canonical B1-B7 presentation includes it.

### 3.6 Hughes/Cresswell modern cross-check

`Strict_Implication/hugn_max.pdf` was used only as a modern cross-check. Its reconstruction lists uniform substitution, substitution of strict equivalents, adjunction, and strict detachment, and it explicitly warns that unrestricted necessitation does not hold in S2 and S3. Nothing from this source was used to replace an L&L schema or basis.

### 3.7 Lewis 1918 and other corpus files

Lewis 1918 was treated as historical background only, consistently with `docs/SOURCE_POLICY.md`. Becker and other corpus items were not needed to override or supplement the canonical formula checks because L&L pp. 493 and 497-501 contain the controlling presentations. No conclusion in this report depends on a semantic reconstruction or on the 1918 typography.

## 4. Language and definition audit

### 4.1 Constructors and levels

| Constructor/notation | M0 status | Source-faithfulness finding |
| --- | --- | --- |
| object atoms | atomic object formulas | Correct representation of L&L proposition letters. The YAML could explicitly mark `atom` as primitive for consistency, but its role is unambiguous. |
| `neg` | primitive connective | Correct. |
| `and` | primitive connective | Correct; diagnostic `∧` and historical juxtaposition are safely separated at rendering level. |
| `poss` | primitive connective | Correct. |
| `or` | first-class defined surface node | Correct and conservative if definition conversion is frozen. |
| `strict_imp` | first-class defined surface node | Correct and desirable: the fishhook remains visible while 11.02 supplies its expansion. |
| `equiv_s` | first-class defined surface node | Acceptable and preferable to overloaded object-language `=`, subject to the deterministic policy below. |
| metalanguage `:=` | not a formula | Correct. |
| plain `=` | forbidden in object formulas | Correct. |
| Box | absent | Correct for the selected native presentation. |

Schema metavariables are correctly represented by `{meta: P}` nodes and are distinct from object atoms. No Box, material implication, or object-language equality occurs in any stored schema AST.

### 4.2 Definition transcription

| Definition | Project expansion | Canonical check | Result |
| --- | --- | --- | --- |
| `DEF_OR` / 11.01 | `P ∨ Q := ∼(∼P ∧ ∼Q)` | L&L p. 123 | Pass |
| `DEF_STRICT_IMP` / 11.02 | `P ⥽ Q := ∼◇(P ∧ ∼Q)` | L&L p. 124 | Pass |
| `DEF_EQUIV_S` / 11.03 | `P ≡ₛ Q := (P ⥽ Q) ∧ (Q ⥽ P)` | L&L p. 124, normalized from overloaded `=` | Formula pass; kernel policy open |

The YAML ASTs, not merely their display strings, have the correct grouping.

### 4.3 Resolution of the `equiv_s` question

The project's intended treatment **is faithful enough in principle for a trusted syntactic checker**, but the treatment in this commit is not yet a specification.

L&L simultaneously (i) list logical equivalence among the primitive ideas, (ii) state 11.03, and (iii) explain why their definition still uses equivalence as the defining relation. A machine checker need not reproduce that overloaded typography. It may instead use a conservative definitional extension:

1. Retain `equiv_s(A,B)` as a genuine object-language *surface* formula node.
2. Declare its deterministic erasure/expansion to be `and(strict_imp(A,B), strict_imp(B,A))`.
3. Keep metalanguage structural equality and definitional equality separate from `equiv_s`.
4. Represent every visible change between a defined node and its expansion by an explicit checked `definition_conversion` certificate node.
5. Check every Lewis rule against the surface AST; never let a rule silently expand or contract definitions to make its premises match.

This is conservative because a definition-conversion node does not assert a new proposition. It certifies a one-occurrence notational conversion whose two endpoints have the same full erasure into `atom`, `neg`, `and`, and `poss`. Feys 30.35, 31.022, and 31.04 provide a strong syntactic precedent for exactly this use of “by definition”.

The architecture is also non-circular with `Sb`. To use a proved pair `A ⥽ B` and `B ⥽ A` as an `Sb` premise, a proof first uses `Ad` to obtain their conjunction, then explicitly contracts that conjunction to `A equiv_s B` by `DEF_EQUIV_S`, and only then applies `Sb`. Definition contraction merely changes registered notation; it does not use `Sb` or presuppose the equivalence theorem it helps display.

What is unacceptable is the current phrase at `spec/language.yaml:181` that the kernel *may* elaborate. Optional, invisible conversion changes certificate validity and formula identity. The chosen policy must be mandatory and uniform.

### 4.4 First-class defined-node architecture

The first-class surface-node architecture is coherent under three invariants:

- proof-node conclusions have exact structural surface identity;
- definition conversion is the only way a visible proof conclusion changes between a defined node and its defining AST;
- a separate deterministic erasure function exists for auditing/conservativity, not for silently rescuing failed rule matches.

The current commit contains all the ingredients for this design but does not impose the invariants. That is the P0 blocker.

## 5. Primitive-rule audit

| Project rule | L&L source | Exact contract check | Result |
| --- | --- | --- | --- |
| `Sa` | p. 125, Substitution (b) | Uniform replacement of each selected proposition letter throughout an asserted theorem. Project label is editorial. | Logical/source pass; certificate payload not frozen. |
| `Sb` | p. 125, Substitution (a) | Given an established strict equivalence, substitute either equivalent expression for the other within an asserted expression. One explicit occurrence per step is a conservative normalization because repeated steps simulate multiple replacements. | Logical/source pass; path grammar not frozen. |
| `Ad` | p. 126, Adjunction | From separately asserted `A` and `B`, assert `A ∧ B` in that order. | Pass. |
| `Smp` | p. 126, Inference | From asserted `A` and `A ⥽ B`, assert `B`, with exact antecedent identity. | Pass. |

The names `Sa`, `Sb`, `Ad`, and `Smp` are correctly recorded as project labels rather than L&L's printed symbolic labels. Feys 30.21-30.24 confirms the mapping.

`B7` is correctly stored as the formula `(P ∧ (P ⥽ Q)) ⥽ Q`; it is not treated as the metalevel rule `Smp`. L&L p. 126 makes the same distinction explicitly.

No necessitation rule, Box constructor, semantic-validity rule, material detachment, tableau rule, sequent rule, or natural-deduction rule has entered the executable core.

The theorem-only restriction is conservative for the present goal. L&L phrase `Sa` and `Sb` so that assumptions may also occur, but a checker that currently accepts only theorems proves no extra theorem. Any later open-assumption consequence relation will require a separate specification.

The remaining `Sa` issue is representational, not historical. A schema-instantiation map acts on schema metavariables; `Sa` acts on object proposition letters in an already checked formula. Those two operations are conflated in the current prose and must be separated before implementation.

## 6. Schema-by-schema audit table

The “normalized parse” column makes every grouping explicit. Each entry was compared against the YAML AST, its display string, and the indicated L&L page.

| Schema | Normalized parse | Primary source | Audit result |
| --- | --- | --- | --- |
| B1 | `(P ∧ Q) ⥽ (Q ∧ P)` | 11.1 pp. 124, 493 | Pass: strict implication between two products. |
| B2 | `(P ∧ Q) ⥽ P` | 11.2 pp. 125, 493 | Pass. |
| B3 | `P ⥽ (P ∧ P)` | 11.3 pp. 125, 493 | Pass. |
| B4 | `((P ∧ Q) ∧ R) ⥽ (P ∧ (Q ∧ R))` | 11.4 pp. 125, 493 | Pass: exactly one associativity direction. |
| B5 | `P ⥽ ∼∼P` | 11.5 pp. 125, 493 | Pass: negations are on the consequent. |
| B6 | `((P ⥽ Q) ∧ (Q ⥽ R)) ⥽ (P ⥽ R)` | 11.6 pp. 125, 493 | Pass: the antecedent is a conjunction of strict implications, not one nested strict implication. |
| B7 | `(P ∧ (P ⥽ Q)) ⥽ Q` | 11.7 pp. 125, 493 | Pass: formula is distinct from metalevel Inference. |
| B8 | `◇(P ∧ Q) ⥽ ◇P` | 19.01 / p. 493 | Pass. |
| A8 | `(P ⥽ Q) ⥽ (∼◇Q ⥽ ∼◇P)` | p. 493 | Pass: both modalized terms are negated possibilities, and their order is contrapositive. |
| C10 | `∼◇∼P ⥽ ∼◇∼(∼◇∼P)` | p. 497 | Pass: YAML's fully expanded prefix form is `strict_imp(neg(poss(neg(P))), neg(poss(neg(neg(poss(neg(P)))))))`. |
| C11 | `◇P ⥽ ∼◇∼◇P` | p. 497 | Pass. |
| C12 | `P ⥽ ∼◇∼◇P` | p. 497 | Pass. |

C10-C12 are the highest-risk transcriptions, and no missing or extra negation was found. C10.1 (`◇◇P ⥽ ◇P`) is correctly not added as a separate primitive. C13 is also correctly outside the target bases.

## 7. S1-S5 basis audit

| System | Canonical historical statement | Executable normalized basis | Result |
| --- | --- | --- | --- |
| S1 | L&L p. 500: B1-B7 | B1-B7 | Pass |
| S2 | L&L p. 500: B1-B8 | B1-B8 | Pass |
| S3 | L&L p. 500: A1-A8 | B1-B7+A8 | Pass as a source-supported normalization; see Section 8. |
| S4 | L&L p. 501: B1-B7+C10 | B1-B7+C10 | Pass |
| S5, primary | L&L p. 501: B1-B7+C11 | B1-B7+C11 | Pass |
| S5, alternative | L&L p. 501: B1-B7+C10+C12 | B1-B7+C10+C12 | Pass as a separately named basis; bridge certificates still required for equivalence/import. |

The resolved YAML bases are exact. `inherit_schemas_from` is safe as schema-set factoring: it produces a target system's own primitive basis. It must not be interpreted as permission to accept a foreign proof node without rechecking that node against the selected target basis.

The intended theorem hierarchy S1-S2-S3-S4-S5 is historically supported. For nonliteral steps in the hierarchy, a future proof library must supply target-basis certificates. CI presently checks only that the hierarchy is declared and marked untrusted without bridges; it does not prove any inclusion.

## 8. Normalized S3 audit

### 8.1 Exact A/B comparison

L&L p. 493 and Parry pp. 137-138 support the following precise classification:

| A-series item | Relation to the B presentation |
| --- | --- |
| A1 | Literal formula match with B1. |
| A2, `QP ⥽ P` | Not a literal B2 copy; Parry identifies the needed S1 theorem as 12.17. |
| A3 | Literal formula match with B3. |
| A4, `P(QR) ⥽ Q(PR)` | Not a literal B4 copy; Parry identifies the needed S1 theorem as 12.5. |
| A5 | Literal formula match with B5. |
| A6 | Literal formula match with B6. |
| A7, `∼◇P ⥽ ∼P` | A distinct S1 theorem; Parry identifies 18.41. |
| A8 | The genuinely additional S3 principle, Parry's 30.1. |

Thus the old shortcut “A1-A6 are formula-for-formula copies of B1-B6” would be false. The wording in the current `README.md`, `docs/FOUNDATIONAL_SPEC_v0.2.md`, `spec/schemas.yaml`, and `spec/systems.yaml` has already been corrected and should be retained.

### 8.2 Adequacy of `S1 + A8`

Parry's p. 137 postulate list plus the p. 138 McKinsey observation gives a basis deductively equivalent to `B1-B7 + A8`. Parry then states how A1-A8 are recovered and derives B8/19.01. This is direct syntactic, not semantic, support. The normalized S3 basis is therefore mathematically safe enough to freeze once the general certificate format is settled.

The fact that future native certificates are pending does not itself invalidate the basis choice: no M1 kernel exists yet with which to check them. It does mean that historical-basis import and theorem-inclusion conveniences must remain disabled until the certificates exist.

### 8.3 Required future S3 bridge corpus

To substantiate the full historical equivalence rather than only cite it, the future checked corpus should include:

1. normalized B-basis proofs of A2, A4, and A7; A1, A3, A5, and A6 need only identity/transcription records;
2. if the project ever exposes historical A1-A8 as a selectable basis, A-basis proofs of the nonliteral B principles B2, B4, and B7;
3. a normalized S3 proof of B8/19.01, following Parry's cited route;
4. primitive-only expansions of every bridge/macro invocation in the target basis.

Until a historical A-basis is executable, these are proof-library obligations, not additional M0 primitive schemas.

## 9. S5 bridge audit

### 9.1 Historical claims

The three requested claims are present at L&L p. 498:

- item (12): C10 is deducible from C11;
- item (13): C12 is deducible from C11;
- item (14): C11 is deducible from C10 and C12.

The proof ideas are syntactic. Item (12) uses C11 with double-negation equivalence; item (13) combines `P ⥽ ◇P` with C11 by the strict syllogism; item (14) substitutes `◇P` into C12 and uses C10.1 to obtain the C11 consequent.

### 9.2 Required qualification

The opening sentence immediately before (12) says these relations are being considered when A1-A8 or B1-B9 are assumed. The current register entries cite p. 498 without recording this qualification and then state the bridges directly over S1. That is incomplete provenance.

This does **not** defeat the selected S5 bases. L&L p. 501 expressly defines S5 from either `B1-B7+C11` or `B1-B7+C10+C12`. In addition, p. 500 places the cited Section 1-4 principles within S1. The correct source record should therefore say:

- p. 498 supplies the displayed derivability arguments in its stated A1-A8/B1-B9 context;
- p. 501 supplies the canonical assertion of the two B1-B7-based S5 presentations;
- the project will not treat either statement as a checked proof certificate.

### 9.3 Bridge architecture

The future bridge library must contain three native target-basis certificates:

1. under `S1+C11`, a proof of C10;
2. under `S1+C11`, a proof of C12;
3. under `S1+C10+C12`, a proof of C11.

The Shen Yuting derivation is an appropriate historical regression for the third. A citation or configuration flag is not a proof node. The current policy correctly says this; the unresolved issue is how the certificate identifies the primary versus alternative S5 basis.

## 10. Proof-certificate and definition-conversion audit

### 10.1 Current status

The broad DAG architecture is sound: conclusions are formulas, dependencies form a DAG, the root must equal the goal, and derived or bridge nodes must expand to kernel-checkable material. However, the current files do not define one shared certificate language:

- `spec/rules.yaml` calls an axiom entry `postulate_instance` with fields `schema_id` and `substitution`;
- `docs/PROOF_CERTIFICATE_SPEC.md` calls it `kind: axiom`, variously using `schema`, `substitution`, and `schema_substitution`;
- the generic rule node uses `parents` and `payload`, while individual rules require `source`, `equivalence_line`, `target_line`, `left_line`, or `antecedent_line`;
- `Sa` is said to substitute “metavariables/object proposition letters”, although those are different syntactic levels;
- the definition-conversion node is expressly only a candidate;
- `system: S5` does not select one of the two primitive bases.

These are not harmless serialization choices. They determine which parent is checked, which syntactic namespace a substitution may affect, and which postulates a proof may invoke.

### 10.2 Acceptable normative definition-conversion mechanism

The following mechanism is precise, conservative, and source-faithful:

```yaml
kind: definition_conversion
parent: n12
definition_id: DEF_EQUIV_S
direction: contract       # exactly expand | contract
occurrence_path: []       # root; otherwise a list of AST field names
conclusion: ...
```

The checker must:

1. resolve `parent` to one already accepted node;
2. resolve `definition_id` to exactly one registered metadefinition;
3. traverse the parent's *surface* formula by the recorded path;
4. match the selected subformula against the source side for the chosen direction using a single consistent metavariable environment;
5. instantiate the other side with that same environment;
6. replace exactly that occurrence and require exact structural identity with `conclusion`;
7. reject nonexistent paths, wrong-side matches, extra fields, metavariables in proof formulas, or any second implicit conversion.

The path should be serialized as a list whose segments are declared child-field names: `[]` for the root, `['arg']` for a unary child, and `['left', ...]` or `['right', ...]` for binary descendants. A dotted form such as `.right.arg` may be rendered for humans but must not be the normative payload.

Every definition must additionally satisfy static checks: the LHS root is its declared first-class defined operator, LHS and RHS have the same metavariable set, repeated metavariables match structurally, and the definition dependency graph is acyclic. The present three definitions meet these conditions; the validator does not yet enforce them.

`definition_conversion` is a trusted certificate kind but not a fifth Lewis inference rule. Its endpoints erase to the same core AST. The trusted-kernel invariant should be phrased as “postulate instances and Sa/Sb/Ad/Smp, modulo checked definitional conversion”.

### 10.3 Safe interaction with `Sb`

`Sb` must require its equivalence parent to have the exact surface root `equiv_s(A,B)`. If a proof currently has `(A ⥽ B) ∧ (B ⥽ A)`, it must first use `DEF_EQUIV_S` contraction. Conversely, `Sb` must not treat metalanguage `:=`, structural AST equality, or equal full erasures as an equivalence premise.

The target path is evaluated in the target parent's surface AST. `Sb` replaces exactly one occurrence in the recorded direction; multiple replacements require multiple checked nodes. Root replacement `[]` is allowed. No definition is expanded while validating `Sb`.

### 10.4 Schema instances versus `Sa`

The certificate contract should make the following distinction normative:

- A `postulate_instance` has no proof parent. Its map has domain exactly the schema metavariables occurring in the registered schema, no extra keys, and object-formula values. Applying it once yields the node conclusion.
- An `Sa` node has exactly one checked theorem parent. Its map is over object atom names occurring in that parent's object formula; it never targets schema metavariables. Unmentioned atoms are fixed. All replacements are simultaneous, one-pass, and nonrecursive into replacement values.

A direct axiom-schema instance is a legitimate primitive certificate entry. If a historical renderer wishes to show a literal postulate followed by `Sa`, it must produce an actual verified expansion, not merely relabel the direct instance cosmetically.

### 10.5 Ad, Smp, and DAG fields

One vocabulary must be selected for parent references. For example, every rule may use `parents` in a rule-defined order, with no parallel `*_line` fields in the logical serialization. The renderer can convert node IDs to line numbers after deterministic topological sorting.

The final contract should also state that node IDs are unique; every parent and root exists; the dependency graph is acyclic; proof formulas contain no schema metavariables; every node is reachable from the root or unreachable nodes are rejected; and the declared goal and root conclusion are structurally identical.

### 10.6 S5 basis identity

The top-level proof metadata must contain an unambiguous basis identity, for example:

```yaml
system: S5
basis: primary
```

or a single stable identifier such as `S5_PRIMARY` / `S5_C10_C12`. Primitive-schema admission is checked only against that basis. The checker must never use the union `{B1-B7,C10,C11,C12}`. Alternatively, M1 may support only the primary basis and leave the alternative basis disabled until the bridge library is installed; that choice must be explicit in M0.

### 10.7 Primitive-only rendering

Two notions should not be conflated:

1. **primitive-proof expansion** removes derived theorem and bridge macros, leaving postulate instances, `Sa`, `Sb`, `Ad`, `Smp`, and checked definition conversions;
2. **formula erasure** expands `or`, `strict_imp`, and `equiv_s` into the primitive connective language.

Historically faithful proof output may retain the fishhook and `equiv_s` while still being primitive at the proof-operation level. A separate fully erased diagnostic view may be offered. The renderer must never hide a visible definition conversion in a proof that otherwise displays surface formulas.

## 11. Validator and CI audit

### 11.1 Executed checks

The checkout was detached at the exact requested SHA before any audit command. The tracked tree was clean before this report was created.

| Check | Exact-candidate result |
| --- | --- |
| `python scripts/validate_spec.py` | Pass: 7 AST constructors, 12 primitive schemas, 4 primitive rules, 5 systems. |
| `python scripts/validate_source_register.py` | Pass: register/spec identifier coverage and status vocabulary checks. |
| bare `pytest` in the base audit runtime | Command unavailable because `pytest` was not installed in that runtime. |
| isolated environment with `PyYAML 6.0.3` and `pytest 8.4.2` | `30 passed in 0.35s`. |
| GitHub Actions on exact SHA | Success: [run 33893929003](https://github.com/Raycaesar/lewis-strict-implication-prover/actions/runs/33893929003), including dependency installation, both validators, and pytest. |

The initial absence of a local `pytest` executable is an environment condition, not a repository failure; the isolated run and exact-commit CI both establish that the suite passes with declared development dependencies.

### 11.2 What `validate_spec.py` establishes

It establishes useful structural invariants:

- the four YAML files exist, parse as mappings, and contain no duplicate mapping keys;
- project/component/version/status metadata agree;
- referenced AST operators are registered and AST field arities are structurally well formed;
- the named forbidden operators are absent;
- metalanguage `:=` and object-language `=` policy flags have the intended values;
- the primitive rule identifiers are exactly `Sa`, `Sb`, `Ad`, and `Smp`;
- unrestricted necessitation is marked disabled;
- the primitive schema identifier set and resolved system-basis sets match hard-coded M0 expectations;
- A1-A7 and B9 are absent from the primitive registry;
- the S5 alternative basis resolves to the intended identifier set;
- theorem inclusion is marked untrusted without bridges.

### 11.3 What it does not establish

It does not establish that:

- any stored schema AST or definition is the formula printed by L&L;
- a schema `display` string denotes its adjacent AST;
- C10-C12 have the right number or placement of negations;
- the prose rule contracts have the right premises or conclusions;
- substitution maps have the intended semantic domain or simultaneous-substitution behavior;
- occurrence paths have a grammar;
- definition conversion is conservative or deterministic;
- any theorem inclusion or S5 bridge is derivable;
- a proof certificate can be parsed or checked;
- the formula-constructor registry is exact rather than merely containing the required seven and excluding three named operators.

### 11.4 What `validate_source_register.py` establishes and does not establish

It checks identifier coverage, basic source IDs, recognized status words, and the presence of explicit blockers. It does not open a source PDF, verify a page, compare a historical formula with a YAML AST, validate source-path existence, verify the advisory summary counts, or close an obligation.

Most importantly, lines 254-260 currently make the validator fail if there are **no** blockers. Consequently, `M0 SOURCE REGISTER VALIDATION: PASS` at this commit positively confirms that the register is still in a pre-freeze state; it cannot be read as a freeze certificate. The validator needs a distinct freeze mode that rejects every `blocked`, `open`, and unresolved P0/P1 status.

### 11.5 Test and workflow limits

The 30 tests mostly restate identifier, flag, and basis-membership assertions. The only general negative tests cover duplicate spec YAML keys and missing spec files. There are no mutation tests for a wrong C10 negation, a malformed rule contract, an implicit definition conversion, a bad path, a schema/object substitution mix-up, or an S5 basis leak.

The workflow's path filters cover `spec/**`, `audit/m0/**`, scripts, tests, `pyproject.toml`, and the workflow itself, but omit `docs/**` and `AGENTS.md`. A change to the foundational or certificate prose can therefore avoid this CI job even though those documents govern M1. This is a CI coverage defect, not evidence against the current formulas.

## 12. Full P0-P3 defect register

### P0-01 - Definition and `equiv_s` conversion semantics are not frozen

1. **Exact location:** `spec/language.yaml:179-184`; `spec/rules.yaml:135-141,167-169`; `docs/ARCHITECTURE.md:64-75`; `docs/PROOF_CERTIFICATE_SPEC.md:249-277`; `audit/m0/foundational_obligations.yaml:28-49,203-209`.
2. **Exact defect:** The executable language permits optional kernel elaboration; the rules file assigns expansion/contraction to parser/renderer behavior; the certificate document proposes but does not adopt a trusted conversion node. No normative rule determines when surface formulas are structurally compared, when definitions may change a proof line, or how `equiv_s` contraction interacts with `Sb`.
3. **Why it matters:** Silent canonicalization and explicit conversion validate different proof DAGs. Optional elaboration could allow `Smp` or `Sb` to succeed after an unrecorded rewrite, violating exact-checking and making independent kernels disagree.
4. **Required repair:** Adopt the explicit one-occurrence `definition_conversion` mechanism in Section 10.2; make surface rule checking exact; define deterministic expansion/erasure and definition well-formedness; remove every “may” or parser/renderer-only account that conflicts with the chosen rule; add positive and malformed-conversion tests.
5. **Changes intended calculus?** No, provided the repair is the conservative definitional extension described here. It changes certificate semantics, which is foundational, but not the intended theorem set.
6. **Re-audit dependency:** Re-audit the revised `language.yaml`, `rules.yaml`, proof-certificate specification, architecture, validators, and definition/Sb tests together. No schema-source re-audit is needed unless a definition AST changes.

### P1-01 - Axiom-schema instantiation and `Sa` have inconsistent, underspecified contracts

1. **Exact location:** `spec/rules.yaml:10-25,118-134`; `docs/PROOF_CERTIFICATE_SPEC.md:35-98`; `audit/m0/foundational_obligations.yaml:211-216`.
2. **Exact defect:** The same node is called `postulate_instance` or `axiom`; fields vary among `schema_id`, `schema`, `substitution`, and `schema_substitution`; generic and rule-specific parent fields disagree. `Sa` may take a “postulate schema” as premise and is said to act on “metavariables/object proposition letters”, despite their explicit syntactic separation. Simultaneous substitution is not specified as one-pass/nonrecursive, and completeness/identity behavior of maps is unclear.
3. **Why it matters:** One checker may admit direct arbitrary axiom instances, another may demand a literal postulate plus `Sa`, and another may accidentally substitute schema metavariables in a theorem. These are different certificate languages and can create unsound or unreplayable proof records.
4. **Required repair:** Select one canonical node vocabulary; define `postulate_instance` as a parentless metavariable instantiation; define `Sa` as a one-parent simultaneous substitution on object atoms only; define required/extra keys, unmentioned-atom identity, and one-pass behavior; reconcile every payload field and renderer example.
5. **Changes intended calculus?** No. It makes the existing axiom-schema normalization and Lewis substitution distinction precise.
6. **Re-audit dependency:** Re-audit the unified certificate grammar, loader-facing schema, positive cases, malformed maps, extra/missing keys, namespace-confusion cases, and historical rendering behavior.

### P1-02 - `Sb` and definition-conversion occurrence paths have no normative grammar

1. **Exact location:** `spec/rules.yaml:44-58`; `docs/PROOF_CERTIFICATE_SPEC.md:102-135,257-270`; `audit/m0/foundational_obligations.yaml:218-223`.
2. **Exact defect:** The rules file shows a dotted renderer path, while the definition example uses `[]`; neither file defines the serialized path type, legal segments, root replacement, traversal through first-class defined nodes, or rejection of malformed/ambiguous paths.
3. **Why it matters:** An occurrence path is security-critical input to the trusted checker. Divergent traversal rules can replace the wrong subformula or allow more than the one licensed occurrence.
4. **Required repair:** Use one list-of-field-names grammar derived from `formula_ast.fields`; define `[]` as root; require exact one-occurrence replacement; forbid traversal beyond atoms/metavariables; use the same grammar for `Sb` and definition conversion; keep dotted paths renderer-only.
5. **Changes intended calculus?** No. One occurrence per node is a conservative certificate normalization of L&L replacement.
6. **Re-audit dependency:** Re-audit the path definition and tests for root, unary, left/right nested, nonexistent, wrong-source, and multi-occurrence attempts after P0-01 is resolved.

### P1-03 - S5 certificates do not identify the governing primitive basis

1. **Exact location:** `spec/systems.yaml:108-139`; `docs/PROOF_CERTIFICATE_SPEC.md:21-31,71-85`; `docs/ARCHITECTURE.md:64-74`.
2. **Exact defect:** S5 has a primary and an alternative primitive basis, but proof metadata records only `system`. “Primitive in the selected system” is therefore ambiguous. Nothing explicitly forbids a checker from taking the union of both basis lists.
3. **Why it matters:** A union would accept C10, C11, and C12 primitively in one proof and would bypass the very bridge certificates the architecture requires. Even without a union, two checkers may choose different defaults.
4. **Required repair:** Add a stable basis identifier to proof metadata and schema-admission checks, or restrict M1 explicitly to `S5_PRIMARY` until the alternative interface is enabled. Never union the bases. Define the source and target basis of every bridge expansion.
5. **Changes intended calculus?** No. It preserves the two L&L presentations while preventing unproved mixed-basis proofs.
6. **Re-audit dependency:** Re-audit `systems.yaml`, proof metadata, axiom admission, wrong-basis rejection tests, and bridge-node semantics.

### P2 defects

| ID | Location | Defect and required repair |
| --- | --- | --- |
| P2-01 | `audit/m0/source_register.yaml:15-24,173-175,205-216,262-285`; `spec/systems.yaml:12-13,70-81,131-139`; `audit/m0/FIRST_PASS_FINDINGS.md:109-118,174-183` | Qualify Parry accurately: his displayed S3 postulate list omits 11.5 because it is derived. Qualify L&L p. 498's (12)-(14) by its A1-A8/B1-B9 preamble and cite p. 501 for the two B1-B7-based S5 presentations. |
| P2-02 | `audit/m0/foundational_obligations.yaml:51-60,132-138`; `audit/m0/SPEC_REPAIR_NOTES.md:7-30` | M0-R01 and M0-N01 remain `repair_needed` although the same commit's repair notes and current files show the repairs were made. Update statuses/evidence and mark `FIRST_PASS_FINDINGS.md` as a historical snapshot or revise its “current” wording. |
| P2-03 | `scripts/validate_spec.py:343-520,524-699`; `scripts/validate_source_register.py:231-265`; `tests/spec/*` | Validation is too shallow for a freeze gate, and the source-register validator currently requires a blocker. Add a freeze mode, exact definition invariants, exact rule-contract checks, display/AST fixtures after human source certification, source-path checks, and negative mutation tests. Do not mistake these checks for mathematical proof. |
| P2-04 | `.github/workflows/m0-spec-validation.yml:5-21` | CI path filters omit `docs/**` and `AGENTS.md`, so governing specification changes need not run M0 validation. Add those paths (and any future frozen-spec lock file) to both push and pull-request triggers. |
| P2-05 | tracked files listed by `git ls-files '*:Zone.Identifier'`; `audit/m0/FREEZE_CHECKLIST.md` repository/CI item | Eight Windows metadata streams remain tracked. Remove them from the next candidate; the ignore rule only prevents future additions and does not untrack existing files. This is not a logical defect but is an explicit freeze-checklist failure. |

Tracked metadata files at the candidate are:

```text
scripts/__init__.py:Zone.Identifier
scripts/validate_spec.py:Zone.Identifier
tests/conftest.py:Zone.Identifier
tests/spec/test_language_spec.py:Zone.Identifier
tests/spec/test_rule_spec.py:Zone.Identifier
tests/spec/test_schema_spec.py:Zone.Identifier
tests/spec/test_system_spec.py:Zone.Identifier
tests/spec/test_validator.py:Zone.Identifier
```

### P3 improvements

| ID | Location | Optional improvement |
| --- | --- | --- |
| P3-01 | `spec/language.yaml:24-28` | Add an explicit status such as `primitive: true` or `kind: atom` to the atom declaration so every constructor's primitive/defined role is machine-explicit. |
| P3-02 | `spec/language.yaml:98-106`; rendering documentation | The ASCII alias `=>` conventionally suggests material implication. It is not unsound because the parser has no material operator, but either remove it or display a prominent parse diagnostic that it means the Lewis fishhook. Name primitive-proof expansion and fully erased formula rendering as separate modes. |

## 13. Exact freeze checklist status

The following evaluates every item in `audit/m0/FREEZE_CHECKLIST.md` against the exact candidate and this audit. “Pass” means the item itself is established; it does not override the overall negative verdict.

### A. Repository and CI

| Item | Status | Evidence |
| --- | --- | --- |
| `python scripts/validate_spec.py` passes | Pass | Executed successfully. |
| `python scripts/validate_source_register.py` passes | Pass | Executed successfully, with the pre-freeze limitation explained above. |
| `pytest` passes | Pass | 30 tests passed in an isolated declared-dependency environment; exact-commit CI also passed. |
| GitHub Actions passes on exact candidate | Pass | Run 33893929003 succeeded for the exact SHA. |
| No tracked `*:Zone.Identifier` files | **Fail** | Eight are tracked. |
| Candidate SHA recorded in final audit | Pass | Recorded at the head of this report. |

### B. Language and definitions

| Item | Status | Evidence |
| --- | --- | --- |
| Primitive/core AST mapping source-verified | Pass | Direct L&L pp. 123-124 check. |
| 11.01 / `DEF_OR` source-verified | Pass | Exact AST match. |
| 11.02 / `DEF_STRICT_IMP` source-verified | Pass | Exact AST match. |
| 11.03 / `DEF_EQUIV_S` source-verified | Pass | Formula verified; normalized use is acceptable in principle. |
| Object-language `=` remains forbidden | Pass | YAML policy and tests agree. |
| `equiv_s` kernel status deterministic/documented | **Fail** | P0-01. |
| Definition conversion deterministic/certificate-checkable | **Fail** | P0-01 and P1-02. |
| No Box constructor/sugar in M0 | Pass | Verified in YAML, schemas, validator, and tests. |

### C. Primitive operations

| Item | Status | Evidence |
| --- | --- | --- |
| `Sa` corresponds to L&L Substitution (b) | Pass | Direct p. 125 check. |
| `Sb` corresponds to L&L Substitution (a) | Pass | Direct p. 125 and Feys 30.24 checks. |
| `Ad` corresponds to Adjunction | Pass | Direct p. 126 check. |
| `Smp` corresponds to Inference | Pass | Direct p. 126 check. |
| All four are project labels | Pass | Corrected in current spec/register. |
| No unrestricted necessitation | Pass | No such rule or Box constructor exists. |
| B7 is not confused with Inference | Pass | Formula and operation are separately specified. |

### D. Schemas

| Item | Status |
| --- | --- |
| B1-B7 ASTs independently checked | Pass |
| B8 AST independently checked | Pass |
| A8 AST independently checked | Pass |
| C10 AST independently checked | Pass |
| C11 AST independently checked | Pass |
| C12 AST independently checked | Pass |
| A1-A7 nonduplication wording accurate | Pass in current prose/spec; audit-register status is stale (P2-02). |
| B9 remains outside M0 | Pass |

### E. Systems and normalization

| Item | Status | Evidence |
| --- | --- | --- |
| S1 = B1-B7 | Pass | L&L p. 500. |
| S2 = B1-B8 | Pass | L&L p. 500. |
| Normalized S3 distinguished from historical A1-A8 | Pass | Prose and YAML distinguish them. |
| Parry support for normalized S3 verified | Pass | Direct pp. 137-138 check, subject to P2-01 wording refinement. |
| S4 = B1-B7+C10 | Pass | L&L p. 501. |
| S5 primary = B1-B7+C11 | Pass | L&L p. 501. |
| S5 alternative = B1-B7+C10+C12 | Pass | L&L p. 501. |
| Theorem inclusion distinct from primitive-basis inheritance | Pass | Policy is correct; certificate basis identity still needs P1-03. |

### F. Certificate architecture

| Item | Status | Reason |
| --- | --- | --- |
| Schema-instance semantics fixed | **Fail** | P1-01. |
| `Sa` payload fixed | **Fail** | Namespace, parent, and simultaneous-map semantics are not fixed. |
| `Sb` occurrence-path grammar fixed | **Fail** | P1-02. |
| `Ad` payload fixed | **Fail** | `parents` versus `left_line`/`right_line` vocabulary is unreconciled. |
| `Smp` payload fixed | **Fail** | `parents` versus named `*_line` vocabulary is unreconciled. |
| Definition-conversion payload fixed | **Fail** | Still expressly a candidate; P0-01. |
| Derived theorem/macro calls never kernel primitives | Pass | Policy is explicit. |
| Bridge calls require checked target-system expansions | Pass | Policy is explicit, though basis metadata must be added. |

### G. Independent audit

| Item | Status |
| --- | --- |
| Work Max audit performed from scratch | Pass: this report. |
| No P0 blocker remains | **Fail** |
| No P1 specification defect remains | **Fail** |
| Final verdict is certification | **Fail** |

**Checklist total:** 37 pass, 12 fail. The freeze condition is not met.

## 14. Minimal repair plan

The following is the smallest repair sequence that can produce a new audit candidate without changing the intended calculus.

1. **Freeze the definition policy.** Replace optional/silent elaboration with the exact explicit conversion mechanism in Section 10.2. Add `definition_conversion` to certificate kinds as a metalinguistic, non-rule node; make all Lewis-rule matching surface-structural.
2. **Unify the certificate schema.** Choose one node vocabulary; separate parentless schema metavariable instantiation from one-parent object-level `Sa`; specify simultaneous substitution; fix Ad/Smp parent payloads and all required/forbidden fields.
3. **Freeze one occurrence-path grammar.** Use list-valued `[]`, `arg`, `left`, and `right` paths for both `Sb` and definition conversion, with one exact replacement per node and complete malformed-path rejection tests.
4. **Name proof bases.** Add a basis identity to S5 certificates or make M1 primary-only. Never allow the union of primary and alternative primitive schemas.
5. **Repair audit provenance/state.** Qualify Parry and L&L p. 498 as described; cite p. 501 for the S1-based S5 alternatives; close the already repaired R01/N01 statuses; update the advisory counts and freeze checklist.
6. **Strengthen the freeze gate.** Add a validator freeze mode that rejects all open/blocked P0/P1 obligations; add definition, path, certificate, wrong-basis, and high-risk AST regression tests; trigger CI on `docs/**` and `AGENTS.md`.
7. **Clean the candidate.** Remove the eight tracked `Zone.Identifier` files, then run both validators and pytest on the new exact SHA and confirm exact-commit GitHub Actions success.
8. **Re-audit the new SHA.** The re-audit may be concentrated on the revised definition/certificate contract, status/provenance repairs, validators, and regressions. Rechecking the unchanged twelve schema ASTs can be a regression confirmation rather than another full source transcription exercise.

No M1 kernel code, search code, proof macro, Box notation, B9 machinery, A1-A7 executable duplicate, or semantic proof rule is needed for this repair.

## 15. Final recommendation

**M1 trusted-kernel implementation may not begin from commit `4931e4daa124587a789ac27b841f499295facf5e`.**

The formal direction should continue. The native logical basis is viable and, at the formula/system level, source-faithful: the definitions, primitive operations, twelve stored schemas, normalized S3 basis, and S1-S5 basis assignments all survived independent checking. The repair burden is sharply bounded to the trusted certificate boundary and associated provenance/validation hygiene.

After the P0 and P1 repairs above are committed, all freeze-gate statuses are made truthful, and a fresh exact-SHA audit finds no remaining blocker, M0 can be certified and M1 can begin. Until then, this candidate must remain `draft_m0`, not `M0 FROZEN`.
