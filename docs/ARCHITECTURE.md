# Architecture
## M0.3 candidate

## 1. Trust layering

```text
historical sources
      ↓
normalized M0 specification
      ↓
trusted M1 kernel
      ↓
untrusted proof library/search
      ↓
renderer / UI
```

Later layers may depend on earlier layers but may not redefine them.

---

## 2. Normalized specification

The executable M0 source of truth is:

```text
spec/language.yaml
spec/rules.yaml
spec/schemas.yaml
spec/systems.yaml
```

The certificate contract is jointly fixed by:

```text
spec/rules.yaml
spec/systems.yaml
docs/PROOF_CERTIFICATE_SPEC.md
```

If these disagree, implementation must stop rather than guess.

---

## 3. Trusted-kernel boundary

The future kernel is intentionally small.

It verifies:

- object formula AST validity;
- system/basis identity;
- primitive postulate-schema instantiation;
- `Sa`;
- `Sb`;
- `Ad`;
- `Smp`;
- explicit `definition_conversion`;
- occurrence paths;
- proof-DAG integrity;
- exact root/goal identity.

The kernel does **not** search for proofs.

### 3.1 Exact surface identity

Primitive Lewis rule checks operate on the visible surface AST.

The kernel must never silently expand `or`, `strict_imp`, or `equiv_s` to make
a rule application succeed.

### 3.2 Definition conversion

Definition expansion/contraction is represented only by the explicit trusted
certificate kind:

```text
definition_conversion
```

It is a checked metalinguistic conversion, not a fifth Lewis inference rule.

### 3.3 Full erasure

A deterministic full-erasure utility may recursively expand definitions into
`atom/neg/and/poss` for:

- conservativity diagnostics;
- regression checking;
- fully erased rendering.

It is not part of primitive-rule matching.

---

## 4. Future kernel package

Provisional M1 structure:

```text
src/lewis_prover/kernel/
├── ast.py
├── spec_loader.py
├── basis.py
├── schema.py
├── substitution.py
├── occurrence_path.py
├── definitions.py
├── rules.py
├── certificate.py
└── checker.py
```

Implementation order after M0 certification:

1. AST and spec loader;
2. basis resolution;
3. schema metavariable instantiation;
4. object-level `Sa`;
5. occurrence paths;
6. `definition_conversion`;
7. `Sb`;
8. `Ad`;
9. `Smp`;
10. DAG checker;
11. deterministic proof linearizer.

No proof search before these are audited by tests.

---

## 5. Basis discipline

Every proof declares:

```text
system
basis_id
```

Allowed basis IDs are defined in `spec/systems.yaml`.

S5 has two separate bases:

```text
S5_PRIMARY_B1_B7_C11
S5_ALT_B1_B7_C10_C12
```

The kernel may never use their union.

A future bridge proof declares:

```text
source_basis_id
target_basis_id
```

and must expand into a certificate valid in the target basis.

---

## 6. Proof library

Future checked data:

```text
proofs/
├── historical/
├── derived/
└── bridges/
```

A stored theorem or macro is untrusted until its expansion is checked.

Citation, historical theorem number, or theorem inclusion does not create a
kernel primitive.

---

## 7. Untrusted search

Future search may use:

- exact theorem lookup;
- schema-directed generation;
- bounded forward saturation;
- backward macro matching;
- bidirectional search;
- best-first ranking;
- semantic pruning;
- external tools or learned heuristics.

All such mechanisms are outside the trusted boundary.

The only route to `PROVED` is kernel acceptance of the resulting native
certificate.

---

## 8. Rendering

Ordinary Lewis-style proof rendering preserves:

- the fishhook;
- `equiv_s`;
- explicit `Df` lines when visible definition conversion occurs.

Two independent display options may exist:

1. **primitive proof operations** — expands derived/bridge macros but preserves
   defined surface notation;
2. **fully erased formulas** — diagnostic expansion of all definitions.

These options must not be conflated.

---

## 9. Search status

Before a separately certified decision procedure:

```text
PROVED
INVALID_CERTIFICATE
NO_PROOF_FOUND_WITHIN_CURRENT_BOUNDS
UNSUPPORTED_SYNTAX
UNSUPPORTED_SYSTEM
INTERNAL_ERROR
```

Search exhaustion never means `NOT_A_THEOREM`.

---

## 10. Change control

Changes to any of the following are foundational:

- formula constructors;
- definition ASTs or conversion semantics;
- primitive postulate ASTs;
- primitive Lewis rules;
- certificate kinds or payload semantics;
- occurrence-path grammar;
- basis IDs or primitive-basis membership.

Such changes require specification revision and focused foundational re-audit.
