# Architecture

## 1. Layered design

The project is divided into five logical layers:

```text
historical sources
      ↓
normalized spec
      ↓
trusted kernel
      ↓
untrusted proof search
      ↓
rendering / UI
```

The direction of trust is one-way: later layers may depend on earlier layers, but they may not redefine them.

---

## 2. Layer A — normalized specification

Files:

```text
spec/language.yaml
spec/rules.yaml
spec/schemas.yaml
spec/systems.yaml
```

Responsibilities:

- define legal formula constructors;
- define parser-level notation;
- define primitive rule contracts;
- define primitive axiom schemas;
- define normalized S1–S5 bases;
- distinguish primitive, defined, and derived material.

No code-level hard-coded duplicate of the calculus should become an independent source of truth.

---

## 3. Layer B — trusted kernel

Provisional future package:

```text
src/lewis_prover/kernel/
├── ast.py
├── schema.py
├── substitution.py
├── replacement.py
├── rules.py
├── certificate.py
└── checker.py
```

The kernel should be small enough to audit line by line.

### Kernel responsibilities

- validate formula ASTs;
- check schema instantiation;
- check substitution maps;
- check replacement-of-equivalents paths;
- check adjunction;
- check strict detachment;
- validate DAG dependencies;
- validate the system in which a primitive schema is available;
- optionally expand/check definitions under a frozen definition policy.

### Kernel non-responsibilities

- deciding which lemma might be useful;
- theorem ranking;
- forward saturation;
- backward proof planning;
- semantic validity;
- UI formatting.

---

## 4. Layer C — proof library

Provisional future package/data:

```text
proofs/
├── derived/
├── bridges/
└── historical/
```

Every stored proof must be kernel-checkable.

A derived macro is an optimization, not a new rule.

---

## 5. Layer D — untrusted search

Provisional future package:

```text
src/lewis_prover/search/
├── lookup.py
├── forward.py
├── backward.py
├── bidirectional.py
├── ranking.py
└── bounds.py
```

Candidate strategies:

1. exact theorem lookup;
2. schema-instance recognition;
3. bounded forward saturation;
4. backward matching against certified macros;
5. bidirectional meet-in-the-middle search;
6. best-first/A*-style search using syntactic cost;
7. theorem-library reuse;
8. system-bridge reuse where certified.

Every candidate proof is sent to the kernel.

---

## 6. Layer E — rendering and UI

Provisional future package:

```text
src/lewis_prover/render/
src/lewis_prover/cli/
src/lewis_prover/web/
```

The UI should eventually support:

- system selection S1–S5;
- formula input;
- proof request;
- concise proof;
- primitive-only expansion;
- exact line justifications;
- system/provenance display;
- optional least-system report once certified searches support it.

Rendering must preserve the strict-implication fishhook and `equiv_s` convention.

---

## 7. Data flow

```text
user input
   ↓
parser
   ↓
formula AST
   ↓
searcher produces candidate proof DAG
   ↓
trusted checker
   ↓
verified proof DAG
   ↓
deterministic linearization
   ↓
Hilbert-style proof output
```

The searcher must never return a user-visible `PROVED` result before checker acceptance.

---

## 8. Proof statuses

Recommended API statuses:

```text
PROVED
INVALID_CERTIFICATE
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
UNSUPPORTED_SYNTAX
UNSUPPORTED_SYSTEM
INTERNAL_ERROR
```

Reserve `NOT_A_THEOREM` for a future certified decision procedure or independently justified refutation mechanism.

---

## 9. Formula identity

The kernel should compare formulas structurally, not by pretty-printed text.

Renderer differences must not affect theorem identity.

Schema metavariables are separate node/types from object-language proposition letters.

---

## 10. Search cost

A later searcher may optimize a cost such as:

```text
proof_lines
+ weighted_dependency_depth
+ weighted_formula_size
+ weighted_substitution_complexity
+ weighted_macro_expansion_cost
```

The exact ranking function is untrusted and may evolve freely without changing logical correctness.

---

## 11. Minimal implementation order

When M1 begins:

1. AST;
2. YAML spec loader;
3. structural parser-independent schema matcher;
4. `Sa`;
5. `Ad`;
6. `Smp`;
7. `equiv_s` and `Sb`;
8. proof-DAG certificate loader;
9. checker;
10. deterministic proof renderer.

Only then begin proof search.
