# Roadmap

## Governing principle

Search may use sophisticated modern algorithms, but every accepted proof must compile to a native syntactic certificate licensed by the selected normalized Lewis system.

---

# M0 — Specification normalization

Current stage: **M0.6 duplicate-key boundary closure candidate**.

### Deliverables

- [x] `spec/language.yaml`
- [x] `spec/rules.yaml`
- [x] `spec/schemas.yaml`
- [x] `spec/systems.yaml`
- [x] foundational documentation skeleton
- [x] source/provenance register for every primitive schema and operation
- [x] first direct source pass against L&L Appendix II and Chapter VI
- [x] structural consistency check between all four YAML files
- [x] source-register referential-integrity validator
- [ ] exact audit of strict-equivalence definition/status
- [ ] exact audit of definition expansion/contraction policy
- [ ] close all M0 blockers in `audit/m0/foundational_obligations.yaml`
- [ ] independent Work Max foundational audit

### Exit criterion

All calculus-level ambiguity is resolved and the specification is marked:

```text
M0 FROZEN
```

No prover code should define a competing calculus.

---

# M1 — Tiny trusted kernel

Implement only what is necessary to verify proof certificates:

- [ ] immutable formula AST
- [ ] YAML spec loader
- [ ] schema matching
- [ ] uniform substitution checker
- [ ] replacement-of-equivalents checker
- [ ] adjunction checker
- [ ] strict-detachment checker
- [ ] proof-DAG loader
- [ ] proof-DAG checker
- [ ] deterministic line-by-line renderer

No automatic theorem search yet.

### Exit criterion

Hand-written certificates can be checked, and malformed variants are reliably rejected.

---

# M2 — Historical regression corpus

Initial targets:

- [ ] a direct S1 theorem such as reflexive strict implication;
- [ ] S1 derivation of historical A7;
- [ ] a nontrivial S1 theorem requiring multiple primitive steps;
- [ ] a theorem characteristically using B8 in S2;
- [ ] a theorem characteristically using A8 in S3;
- [ ] an S4 result using C10;
- [ ] an S5 result using C11;
- [ ] the C10 + C12 → C11 Shen-related bridge/proof;
- [ ] negative certificate tests for each rule.

### Exit criterion

The corpus passes in primitive-only mode.

---

# M3 — Certified derived-rule library

Import and reconstruct useful proof patterns from Feys, Parry, McKinsey, L&L, and later literature.

Every macro must expand to a checked primitive certificate.

Targets include:

- strict transitivity patterns;
- equivalence manipulation;
- useful modal transformations in diamond notation;
- basis-bridge lemmas;
- frequently needed substitution templates.

---

# M4 — Automatic proof search

Implement a portfolio searcher:

- exact theorem lookup;
- schema-directed matching;
- bounded forward saturation;
- goal-directed backward macro search;
- bidirectional search;
- best-first ranking;
- proof caching.

Search is untrusted.

### Required failure message

```text
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
```

until a decision procedure is separately certified.

---

# M5 — System bridges and least-system analysis

Build checked theorem-inclusion infrastructure.

Targets:

- S1 → S2
- S2 → S3
- S3 → S4
- S4 → S5
- S5 primary basis ↔ alternative C10+C12 basis

Then support:

```text
least verified system for formula
```

without conflating theorem inclusion with primitive-basis inheritance.

---

# M6 — User interface

After kernel/search APIs stabilize:

- system selector;
- formula editor;
- proof button;
- line-by-line Hilbert output;
- concise / primitive-only toggle;
- provenance panel;
- search-bound diagnostics;
- export to plain text / Markdown / LaTeX.

---

# Later milestones

Possible later work:

- syntactic decision procedures where historically/mathematically justified;
- proof minimization;
- interactive proof construction;
- article-oriented LaTeX export;
- B9/existence extensions;
- alternative historically certified presentations;
- web playground.


---

# M0.3 — Foundational certificate repair

The first Work Max audit of commit
`4931e4daa124587a789ac27b841f499295facf5e` passed the formula/system layer but
did not certify the trusted certificate boundary.

M0.3 repairs:

- [x] deterministic explicit `definition_conversion`;
- [x] exact surface-AST rule matching;
- [x] strict separation of `postulate_instance` from object-level `Sa`;
- [x] one normative occurrence-path grammar;
- [x] stable basis IDs, including separate S5 primary/alternative bases;
- [x] source/provenance qualification for Parry and L&L p. 498;
- [x] audited AST fingerprint lock;
- [x] freeze-readiness validator mode;
- [x] CI coverage for governing docs/AGENTS;
- [x] Windows metadata cleanup tooling;
- [ ] exact candidate commit uploaded and CI green;
- [ ] focused Work Max closure recheck;
- [ ] `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`.

M1 remains forbidden until the final item is achieved.


# M0.4 — second closure repair

Closes closed-world certificate serialization, operational S5 bridge direction, complete Parry provenance, freeze-gate mutation coverage, repair-log vocabulary, and fingerprint metadata. Awaiting exact-SHA second closure recheck before M1.


# M0.5 — single-authority freeze repair

Remove duplicate certificate-semantics mirrors, make `canonical_certificate_contract` the sole machine-readable authority, fingerprint the entire contract, replay all nine M0.4 accepted mutations, and run one narrow P2 closure recheck. M1 remains gated.


# M0.6 — duplicate-key boundary restoration

Restores the duplicate mapping/object-key rejection invariant lost during the M0.5 single-authority migration, defines the canonical strict JSON decoding boundary, adds document-level conformance fixtures, and reopens the closed-world serialization obligation pending one narrow exact-SHA recheck. No formula, definition, basis, or S5 bridge change.
