# Lewis S1-S5 Native Syntactic Prover
## Foundational specification v0.1

**Status:** architectural/foundational draft after first source pass  
**Canonical historical basis:** C. I. Lewis and C. H. Langford, *Symbolic Logic* (1932), Chapter VI and Appendix II.  
**Primary design constraint:** every final proof certificate must reduce to the axioms, definitions, and rules licensed by the selected Lewis system. No Kripke semantics, matrix validity, tableau calculus, sequent calculus, or modern normal-modal proof system may occur as an unexpanded proof step.

---

## 1. Source policy

### 1.1 Canonical source

For the definition of the object language, primitive operations, postulates, and S1-S5, the canonical source is **Lewis & Langford 1932**.

Relevant loci in the supplied scan:

- Chapter VI, pp. 123-126: primitive ideas, definitions 11.01-11.03, postulates 11.1-11.7, and the rules of substitution, adjunction, and inference.
- Chapter VI, Section 5, beginning p. 166: the Consistency Postulate B8.
- Appendix II, pp. 492-501: comparison of the A- and B-postulate sets and the explicit definitions of S1-S5.

The 1959 Dover printing in the supplied PDF is a reprint of the 1932 second edition; page references below are printed-book pages.

### 1.2 Secondary syntactic sources

These sources are used for derived rules, proof patterns, bridge proofs, and search heuristics, but **never override the L&L basis**:

1. **Robert Feys, *Modal Logics***: especially §§30-37 (S1), §40 onward (S2), §50 onward (S3), §60 onward (S4), and §70 onward (S5). This is the most systematic source for machine-oriented derived rules and proof patterns.
2. **W. T. Parry (1939), “Modalities in the Survey System of Strict Implication”**: especially useful for S3, its relation to S1/S2, explicit theorem derivations, Becker-style rules, and extensions to S4/S5.
3. **Hughes/Cresswell, chapter “Strict Implication”** in the supplied `hugn_max.pdf`: useful as a modern cross-check and for alternative axiomatizations, but not canonical. It modernizes notation and omits/replaces some historically redundant material.
4. **McKinsey (1934)**: useful for redundancy information and proof minimization, not for changing the canonical L&L basis.
5. **Lewis 1918**: historical comparison only. It is not the notation or basis used by the prover.

### 1.3 Import rule for later literature

Every imported theorem or derived rule must carry:

- source provenance;
- source theorem/rule number where available;
- a declared minimal source system;
- a machine-checkable expansion into the canonical L&L basis of the target system.

A theorem from Feys/Parry/Hughes is not trusted merely because the source states it. It enters the fast theorem library only after the proof checker validates its expansion.

---

## 2. Canonical language and notation

### 2.1 L&L primitive/undefined ideas

Chapter VI starts from:

- propositional variables `p, q, r, ...`;
- negation `~P`;
- logical product `PQ` (conjunction);
- possibility/self-consistency `◇P`;
- logical equivalence `P = Q`.

Strict implication is introduced by definition 11.02:

`P ↝ Q  =df  ~◇(P ~Q)`

where juxtaposition is conjunction.

For implementation, `StrictImp(P,Q)` is retained as a first-class AST node for efficient matching and readable certificates, but is tagged as **defined L&L notation**, not as an independent primitive semantic operator.

### 2.2 Other defined notation

The core parser/renderer should support:

- disjunction `P ∨ Q` (L&L 11.01);
- strict implication `P ↝ Q` (L&L 11.02);
- strict/logical equivalence `P = Q` (connected with 11.03);
- necessity `□P := ~◇~P` as an implementation abbreviation;
- material implication `P → Q := ~(P ~Q)` when needed for later theorem libraries.

The checker must be able to expand and contract definitions explicitly in `primitive-only` proof mode.

### 2.3 Input syntax

Recommended modern UI syntax:

- `~p` or `¬p`
- `p & q` or `p ∧ q`
- `p | q` or `p ∨ q`
- `<>p` or `◇p`
- `[]p` or `□p`
- `p => q` or `p ↝ q` for **strict implication**
- `p -> q` for material implication
- `p <=> q` for strict/logical equivalence

An optional `Lewis notation` parser may later accept dot punctuation and the historical strict-implication glyph, but the first implementation should require parentheses rather than reproduce Principia-style dots in user input.

---

## 3. Canonical primitive proof operations

All S1-S5 share the Chapter VI operations.

### R1. Uniform substitution

Any proposition/formula expressible in the language may be uniformly substituted for a propositional variable throughout a postulate or established theorem.

Certificate data must record the substitution map, e.g.

`{p := (r & s), q := <>t}`.

### R2. Replacement of equivalents

If `P = Q` has been established, `P` may replace `Q`, or `Q` may replace `P`, at a specified occurrence inside an established formula.

A certificate must record:

- the line establishing `P = Q`;
- rewrite direction;
- structural path of the replaced occurrence.

This avoids an ambiguous justification such as merely “replacement”.

### R3. Adjunction

From asserted `P` and asserted `Q`, assert `PQ`.

### R4. Inference / strict detachment

From asserted `P` and asserted `P ↝ Q`, assert `Q`.

**Critical restriction:** there is no primitive unrestricted necessitation rule in the L&L basis. In particular the engine must never silently use `P / □P` in S1, S2, or S3. No such rule will be enabled in S4/S5 either unless a fully verified L&L-native derived-rule expansion is later supplied.

---

## 4. L&L canonical systems

The canonical system descriptions are those stated explicitly in Appendix II, pp. 500-501.

### 4.1 S1

**Basis:** B1-B7.

In modern parenthesized notation:

- **B1** `(p & q) ↝ (q & p)`
- **B2** `(p & q) ↝ p`
- **B3** `p ↝ (p & p)`
- **B4** `((p & q) & r) ↝ (p & (q & r))`
- **B5** `p ↝ ~~p`
- **B6** `((p ↝ q) & (q ↝ r)) ↝ (p ↝ r)`
- **B7** `(p & (p ↝ q)) ↝ q`

This is the system that L&L Appendix II explicitly calls **S1**.

### 4.2 S2

**Basis:** B1-B8.

- **B8** `◇(p & q) ↝ ◇p`

L&L calls B8 the **Consistency Postulate**.

### 4.3 S3

**Canonical 1932 basis:** A1-A8 (the amended Survey basis), not “S2 plus one axiom” as a primitive definition.

- **A1** `(p & q) ↝ (q & p)`
- **A2** `(q & p) ↝ p`
- **A3** `p ↝ (p & p)`
- **A4** `p & (q & r) ↝ q & (p & r)`
- **A5** `p ↝ ~~p`
- **A6** `((p ↝ q) & (q ↝ r)) ↝ (p ↝ r)`
- **A7** `~◇p ↝ ~p`
- **A8** `(p ↝ q) ↝ (~◇q ↝ ~◇p)`

Later syntactic sources give equivalent or more convenient bases for S3. These may be used by the search engine only as **certified macro bases** whose applications expand back to A1-A8 plus R1-R4.

### 4.4 S4

**Canonical 1932 basis:** B1-B7 + C10.

In box notation, C10 is the strict form of positive introspection / modal axiom 4:

- **C10** `□p ↝ □□p`

Equivalently in L&L's possibility/negation notation:

`~◇~p ↝ ~◇~ ~◇~p`.

L&L states that A8 and B8 are derivable in S4, so S4 contains the theorems of S3 although its primitive basis is not literally A1-A8.

### 4.5 S5

L&L gives two equivalent bases:

**Primary canonical basis for this prover:** B1-B7 + C11.

- **C11** `◇p ↝ □◇p`

Equivalent L&L form: `◇p ↝ ~◇~◇p`.

**Alternative certified basis:** B1-B7 + C10 + C12, where

- **C12** `p ↝ □◇p`.

The primary implementation should store C11 as the primitive S5 extension and treat the C10+C12 basis as an alternative source basis with a bridge proof.

---

## 5. The B9 existence postulate must be separated from the propositional core

Appendix II distinguishes B9 as an **Existence Postulate**. It contains propositional existential quantification and is independent of B1-B8.

Therefore the default theorem prover for propositional/modal formulas must implement:

- `S1`, `S2`, `S3`, `S4`, `S5` **without B9**;
- a later optional extension, e.g. `S1+E`, ..., `S5+E`, if quantified propositional/existence theorems are to be supported.

This is not merely an optimization. It prevents the propositional parser and proof checker from being contaminated by a second-order/propositional-quantification feature irrelevant to ordinary S1-S5 theorem proving.

---

## 6. A crucial architectural consequence: theorem inclusion is not basis inheritance

The engine must not implement the systems as a simple class chain

`S1 -> S2 -> S3 -> S4 -> S5`

where each child merely adds primitive axioms.

Historically/canonically:

- S1 uses B1-B7;
- S2 uses B1-B8;
- S3 uses A1-A8;
- S4 uses B1-B7+C10;
- S5 uses B1-B7+C11 (or B1-B7+C10+C12).

Yet theorem-inclusion results establish the familiar increasing hierarchy.

Hence the implementation needs two different relations:

1. `primitive_basis(system)`;
2. `theorem_inclusion(system_a, system_b)` backed by **bridge certificates**.

A theorem proved in S2 may be reused in an S3 search only if either:

- it is reproved under A1-A8; or
- the required S2 basis principles have already been certified as derived in S3.

The same applies to S3 -> S4 and S4 -> S5.

This is one of the most important invariants of the whole project.

---

## 7. Proof object and proof checker

### 7.1 Proof DAG

Internally a proof is a DAG, not a printed sequence.

Each node contains at least:

```text
ProofNode
  id
  conclusion: Formula
  justification: Justification
  premises: [ProofNodeID]
  system: SystemID
  provenance: optional SourceRef
```

### 7.2 Justification variants

```text
AxiomInstance(B6, substitution)
UniformSubstitution(line, substitution)
Adjunction(line1, line2)
StrictDetachment(lineP, linePStrictQ)
EquivalentReplacement(lineFormula, lineEquiv, path, direction)
DefinitionExpansion(definition_id, path)
DefinitionContraction(definition_id, path)
DerivedMacro(macro_id, premises, expansion_certificate)
ImportedTheorem(theorem_id, expansion_certificate)
```

### 7.3 Independent checker

The checker must not share proof-search logic. It accepts only a proof DAG and a selected system and verifies every node locally.

A successful run ends with a small trusted-kernel statement:

`VERIFIED: target is derivable in canonical L&L S_n`.

The trusted kernel should be deliberately small: parser/AST well-formedness, schema matching, R1-R4, definitions, and the selected primitive axiom set.

---

## 8. Proof rendering modes

### 8.1 Canonical detailed mode

Every line cites the exact primitive reason:

```text
1. ((p=>q) & (q=>r)) => (p=>r)        B6
2. p=>q                                ...
3. q=>r                                ...
4. (p=>q) & (q=>r)                     Adjunction 2,3
5. p=>r                                Inference 4,1
```

### 8.2 Concise historical mode

Certified derived rules/theorems may be named, e.g. “strict transitivity”, with a link/expansion available.

### 8.3 Primitive-only mode

All derived rules and imported lemmas are recursively expanded until every leaf is a canonical L&L postulate instance and every edge is R1-R4 or a definition step.

This is the definitive audit mode.

---

## 9. Search architecture

The search engine may be sophisticated, but the certificate must remain purely L&L-syntactic.

### 9.1 Search portfolio

Run several coordinated search procedures:

1. exact theorem/instance lookup;
2. goal-directed schema matching;
3. backward macro search;
4. relevance-bounded forward saturation;
5. bidirectional meet-in-the-middle search;
6. proof-carrying equivalence rewriting;
7. theorem-library landmark search.

The first proof found is checked immediately by the independent kernel.

### 9.2 Relevance universe

Blind enumeration of all substitutions is impossible. For a target `T`, construct a bounded relevance universe containing:

- subformulas of `T`;
- negations of relevant formulas;
- modal complements needed by definitions (`◇P`, `~◇~P`);
- conjunctions required by B6/B7 and adjunction;
- strict implications generated by unification against axiom/macro conclusions;
- formulas occurring in selected theorem-library landmarks.

Expansion is iterative and cost-bounded.

### 9.3 Axiom-schema unification

Axioms are stored as metavariable patterns. The engine performs structural unification rather than enumerating arbitrary substitutions.

Example: matching the B6 consequent `P ↝ R` to a target fixes two metavariables immediately and leaves only the intermediate `Q` to synthesize.

### 9.4 Derived macros

Common L&L-native patterns should be registered as proof-producing macros.

Example: strict transitivity from `P↝Q` and `Q↝R`:

1. instantiate B6;
2. adjunction of the two premises;
3. strict detachment.

Search treats this as one edge, but the certificate contains the three-step expansion.

Feys is particularly valuable for building this macro library.

### 9.5 Proof-carrying equality saturation

Replacement of equivalents is essential but can explode combinatorially. Use an e-graph-like index only as a **search structure**. Every equivalence edge must retain the theorem/certificate that licenses the rewrite.

The checker never trusts e-graph equivalence by itself.

### 9.6 Best-first / A* cost

Candidate proof states receive costs based on:

- number of primitive proof steps;
- generated formula size;
- number/complexity of substitutions;
- modal depth increase;
- number of equivalence rewrites;
- distance from target subformula vocabulary.

Iterative deepening should cap formula size and modal depth before widening.

---

## 10. Search modes and the “no other means” requirement

The core release should have a mode named, for example, `native-syntax`:

- no semantic oracle;
- no matrix checker used to assert theoremhood;
- no Kripke model search;
- no tableau/sequent proof translated into Hilbert form;
- only direct search through the L&L calculus plus previously certified L&L-native macros/theorems.

Later, a separate diagnostic mode may use semantics to produce countermodels or guide search, but such a component must be outside the trusted proof path and clearly disabled in `native-syntax` mode.

Search failure must never be reported as non-theoremhood merely because a bounded Hilbert search failed.

Possible statuses:

- `PROVED`
- `NO PROOF FOUND WITHIN CURRENT BOUNDS`
- `UNKNOWN`

A `NOT A THEOREM` status is allowed only if a separately justified decision procedure has been adopted for that mode; it is not part of v1 native syntax.

---

## 11. Theorem library

Store each theorem as a proof-carrying object:

```text
TheoremRecord
  canonical_formula
  source_formula
  minimal_verified_systems
  source_refs
  proof_certificate_by_system
  tags
  search_signature
```

Initial high-priority corpus:

1. L&L Chapter VI theorems 12.1-18.92 (S1 core);
2. L&L Section 5 theorems 19.02-19.92 (S2);
3. Parry 1939 S2/S3 theorems and Becker-style derived rules;
4. Feys §§31-37 derived S1 rules/theorems;
5. Feys S2/S3/S4/S5 bridge theorems;
6. explicit Appendix II bridge results needed for theorem inheritance.

Do not import a theorem into `verified_library` until its primitive certificate passes the checker.

---

## 12. Minimal-system analysis

When the user selects S5 and asks for a theorem, the UI may optionally attempt to identify the least verified Lewis system.

However the algorithm must respect canonical bases:

```text
prove in S1
prove in S2
prove in S3
prove in S4
prove in S5
```

or reuse already certified inclusion bridges.

Output may say:

```text
Selected system: S5
Proved in: S2
Therefore also available in S3, S4, S5 via verified bridge library.
```

No hierarchy claim should be based merely on a hard-coded enum ordering.

---

## 13. Historical provenance and reproducibility

Every theorem/proof should be able to display:

- selected canonical system;
- canonical primitive basis;
- whether B9 is disabled/enabled;
- definitions used;
- imported historical lemmas;
- source locations;
- fully expanded primitive proof.

This permits the tool to serve not only as a theorem prover but also as a historical proof-reconstruction environment.

---

## 14. Proposed repository layout

```text
lewis-strict-prover/
├── README.md
├── docs/
│   ├── foundational_spec.md
│   ├── source_policy.md
│   ├── notation.md
│   └── search_design.md
├── spec/
│   ├── language.yaml
│   ├── rules.yaml
│   ├── s1.yaml
│   ├── s2.yaml
│   ├── s3.yaml
│   ├── s4.yaml
│   └── s5.yaml
├── src/
│   ├── syntax/
│   ├── kernel/
│   ├── proof/
│   ├── search/
│   ├── library/
│   └── ui/
├── data/
│   ├── sources/
│   ├── theorem_index/
│   └── bridge_proofs/
└── tests/
    ├── kernel/
    ├── historical/
    ├── regression/
    └── system_separation/
```

The repository should not be opened around a large implementation yet. First freeze `spec/` and the trusted-kernel interface.

---

## 15. First implementation milestones

### M0. Source normalization

- transcribe and double-check L&L B1-B8, A1-A8, C10-C12;
- transcribe Chapter VI definitions and rules;
- resolve exact precedence/parenthesization of all postulates;
- record source pages and scans.

### M1. Tiny trusted kernel

Implement only:

- AST;
- parser/printer;
- schema matching;
- R1-R4;
- definitions;
- system-specific primitive axiom lookup;
- proof DAG checker.

No automatic proof search yet.

### M2. Historical regression proofs

Encode a small set of L&L/Feys/Parry proofs manually and verify them through the kernel.

Targets should include:

- identity `p ↝ p`;
- strict transitivity as a derived rule;
- representative equivalence-replacement proofs;
- one S2-only theorem using B8;
- one S3 theorem using A8;
- derivation of an S3 principle in S4;
- C10/C12 -> C11 in S5 (the Shen-related bridge).

### M3. Derived-rule compiler

A macro is accepted only if its expansion checks. Build the first rule library from Feys §§31-37.

### M4. Searcher v1

Implement relevance-bounded forward + backward + best-first search.

### M5. Bridge library

Machine-verify the theorem-inclusion bridges S1 -> S2 -> S3 -> S4 -> S5 without conflating their primitive bases.

### M6. UI

Only after the kernel/search interface is stable, add the browser UI.

---

## 16. Immediate research tasks before Codex implementation

The next source pass should answer and formally record:

1. exact L&L treatment of logical equivalence `=` as primitive idea versus defined relation, and the precise checker representation of 11.03;
2. exact formation conditions implicit in Chapter VI;
3. complete derivation status of B5 after McKinsey, while retaining it in the canonical 1932 basis;
4. explicit primitive bridge proofs:
   - B1-B8 from A1-A8 (S3 contains S2);
   - A8 and B8 in S4;
   - C10 in S5;
   - C10+C12 -> C11 and conversely the relevant S5 basis equivalences;
5. which Feys derived rules can be converted into compact, reusable proof templates without importing his alternative primitive basis;
6. which Parry 1939 S3 proofs are especially useful as search landmarks;
7. whether a guaranteed syntactic decision/reconstruction method is available for any of S1-S5 without violating the project’s native-proof requirement.

Only after these points are settled should Codex be asked to implement more than the trusted kernel.

---

## 17. Current architectural verdict

The project is technically viable, but its correctness depends on maintaining a strict separation among:

1. **canonical historical basis** (L&L 1932);
2. **derived syntactic machinery** (Feys, Parry, later reconstructions);
3. **search heuristics**;
4. **the small proof-checking kernel**.

The most important design principle is:

> **Search may use sophisticated modern algorithms; every accepted proof must compile down to an L&L-native syntactic certificate for the selected system.**

That principle should be enforced structurally by the software rather than left as a convention.
