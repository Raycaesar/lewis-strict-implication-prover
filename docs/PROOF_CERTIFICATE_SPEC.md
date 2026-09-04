# Proof Certificate Specification
## M0.3 candidate — normative trusted-boundary contract

**Status:** M0 closure-audit candidate  
**Scope:** certificate semantics only; this document does not implement the M1 kernel.

This document is normative for what a future trusted checker may accept.

---

## 1. Central invariant

Every accepted theorem certificate consists only of:

1. parentless instances of primitive postulate schemas admitted by the selected `basis_id`;
2. the four Lewis operations `Sa`, `Sb`, `Ad`, and `Smp`;
3. explicit checked `definition_conversion` nodes.

`definition_conversion` is **not** a fifth Lewis inference rule. It is trusted
metalinguistic checking of the registered definitions 11.01–11.03.

No primitive Lewis rule may silently expand or contract a definition.

\[
\boxed{\text{Lewis rule matching is exact on the visible/surface AST}}
\]

---

## 2. Proof-level metadata

A certificate has exactly these logical top-level fields:

```yaml
proof_id: example
system: S5
basis_id: S5_PRIMARY_B1_B7_C11
goal: ...
root: n17
nodes: ...
```

### 2.1 `system`

One of:

```text
S1
S2
S3
S4
S5
```

### 2.2 `basis_id`

Required for **every** proof.

Allowed pairs are declared in `spec/systems.yaml`:

```text
S1  -> S1_B1_B7
S2  -> S2_B1_B8
S3  -> S3_B1_B7_A8
S4  -> S4_B1_B7_C10
S5  -> S5_PRIMARY_B1_B7_C11
S5  -> S5_ALT_B1_B7_C10_C12
```

A checker rejects a mismatched `(system, basis_id)` pair.

For S5 the checker must never form the union of the primary and alternative
primitive bases.

### 2.3 Goal and root

`root` names one proof node.

The root conclusion must be structurally identical to `goal`.

---

## 3. Proof DAG

`nodes` is a mapping from unique node IDs to nodes.

Each node has exactly:

```yaml
conclusion: <object-formula AST>
justification: <one normative justification object>
```

No schema metavariable node `{meta: ...}` is permitted inside a proof formula.

The checker must reject a certificate unless:

- every node ID is unique;
- every referenced parent exists;
- `root` exists;
- the dependency graph is acyclic;
- every node is reachable from `root`;
- every node is accepted after its parents;
- root conclusion equals the declared goal exactly.

Line numbers are **not** part of the logical certificate. They are assigned only
after deterministic topological linearization.

---

## 4. Justification vocabulary

`justification.kind` is exactly one of:

```text
postulate_instance
Sa
Sb
Ad
Smp
definition_conversion
```

There is no generic `axiom`, `rule_application`, `*_line`, or hidden payload
vocabulary in the normative serialization.

Derived theorem calls and bridge calls belong to a later proof-library layer.
They are never accepted as primitive kernel kinds; they must expand before the
kernel boundary.

---

## 5. `postulate_instance`

A postulate instance is parentless.

```yaml
conclusion: ...
justification:
  kind: postulate_instance
  schema_id: B6
  schema_substitution:
    P: ...
    Q: ...
    R: ...
```

### 5.1 Namespace

`schema_substitution` acts only on schema metavariables in the registered
postulate AST:

```text
P, Q, R, ...
```

It never acts on object atom names as object-level `Sa`.

### 5.2 Domain

The map domain is **exactly** the set of schema metavariables occurring in that
schema.

Reject:

- missing keys;
- extra keys;
- non-formula values;
- values containing schema metavariable nodes.

### 5.3 Check

The checker:

1. verifies that `schema_id` belongs to the exact primitive schema set of
   `basis_id`;
2. instantiates the schema once with the recorded map;
3. requires exact surface-AST identity with `conclusion`.

A direct schema instance is a legitimate primitive proof entry. A renderer must
not cosmetically call it `Sa`. If a historical presentation wants a literal
postulate followed by substitution, it must contain an actual checked `Sa`
node.

---

## 6. `Sa` — uniform object-level substitution

```yaml
conclusion: ...
justification:
  kind: Sa
  parents: [n4]
  atom_substitution:
    p: ...
    q: ...
```

### 6.1 Namespace

The keys are **object atom names** occurring in the parent theorem.

They are not schema metavariables.

### 6.2 Semantics

Substitution is:

- simultaneous;
- one-pass;
- nonrecursive into replacement values;
- uniform at every occurrence of each selected atom.

Atoms not listed are fixed.

The map must be non-empty. Keys not occurring in the parent formula are
rejected.

### 6.3 Check

The parent must already be a checked theorem node.

The checker applies the object-atom map to the parent surface AST and requires
exact identity with the conclusion.

No definition is expanded or contracted during this check.

---

## 7. Normative occurrence-path grammar

The same grammar is used by `Sb` and `definition_conversion`.

Logical serialization is a list of field-name strings:

```yaml
occurrence_path: []
occurrence_path: [arg]
occurrence_path: [right, arg]
```

### 7.1 Root

```yaml
[]
```

selects the whole formula.

### 7.2 Legal segments

Only:

```text
arg
left
right
```

are legal path segments.

At each step the segment must name an actual **formula-valued child field** of
the current surface AST node.

Thus:

- `neg`, `poss` expose `arg`;
- `and`, `or`, `strict_imp`, `equiv_s` expose `left`, `right`;
- `atom` exposes no traversable formula child.

The atom payload `name` is never a path segment.

### 7.3 Surface traversal

First-class defined nodes are traversed exactly as displayed. Path traversal
never expands a definition.

### 7.4 Rejection

Reject:

- dotted strings as logical payloads;
- integer indices;
- unknown segments;
- paths through `atom.name`;
- paths that leave the tree.

A dotted form such as `.right.arg` is renderer-only.

---

## 8. `Sb` — substitution of strict equivalents

```yaml
conclusion: ...
justification:
  kind: Sb
  parents: [n_equiv, n_target]
  direction: left_to_right
  occurrence_path: [right, arg]
```

`parents` is ordered:

1. equivalence parent;
2. target parent.

### 8.1 Equivalence premise

The first parent must have exact visible root:

```text
equiv_s(A,B)
```

The following do **not** count:

- metalanguage `=`;
- metalanguage `:=`;
- structural equality of two ASTs;
- equal full erasures;
- the conjunction `(A strict_imp B) and (B strict_imp A)` before explicit
  contraction by `DEF_EQUIV_S`.

### 8.2 Direction

Exactly:

```text
left_to_right
right_to_left
```

### 8.3 Replacement

The selected target occurrence must be structurally identical to the source
side for that direction.

Exactly one occurrence is replaced per `Sb` node.

Root replacement is allowed.

Multiple replacements require multiple checked `Sb` nodes.

No implicit definition conversion occurs while checking `Sb`.

---

## 9. `Ad` — adjunction

```yaml
conclusion: ...
justification:
  kind: Ad
  parents: [n_left, n_right]
```

The conclusion must be exactly:

```text
and(conclusion(n_left), conclusion(n_right))
```

in that order.

No hidden commutativity or reassociation is allowed.

---

## 10. `Smp` — L&L Inference / strict detachment

```yaml
conclusion: ...
justification:
  kind: Smp
  parents: [n_antecedent, n_implication]
```

The first parent concludes `A`.

The second parent must have exact visible form:

```text
strict_imp(A,B)
```

with an antecedent structurally identical to the first parent's conclusion.

The node concludes exactly `B`.

No definition is implicitly expanded to make the antecedents match.

B7 is an object-language postulate schema and is not this metalevel operation.

---

## 11. `definition_conversion`

```yaml
conclusion: ...
justification:
  kind: definition_conversion
  parents: [n12]
  definition_id: DEF_EQUIV_S
  direction: contract
  occurrence_path: []
```

The parent list has exactly one element.

### 11.1 Direction

Exactly:

```text
expand
contract
```

- `expand`: match the selected occurrence against the definition LHS and replace
  it by the instantiated RHS.
- `contract`: match the selected occurrence against the definition RHS and
  replace it by the instantiated LHS.

### 11.2 Definition matching

The checker must:

1. resolve `definition_id` to one registered metadefinition;
2. traverse the parent surface AST by `occurrence_path`;
3. match the selected occurrence using one consistent metavariable environment;
4. require repeated metavariables to match structurally;
5. instantiate the opposite side with the same environment;
6. replace exactly one selected occurrence;
7. require exact structural identity with the node conclusion.

No second definition conversion is performed implicitly.

### 11.3 Why this is not a fifth Lewis rule

Definition conversion does not assert a new consequence relation. It checks a
registered metalinguistic abbreviation/definition.

For example:

```text
(A ⥽ B) ∧ (B ⥽ A)
A ≡ₛ B                    Df 11.03
```

Only after this explicit contraction may the second line serve as the
equivalence premise of `Sb`.

This avoids circularity: `DEF_EQUIV_S` contraction does not use `Sb`.

---

## 12. Definition well-formedness

Before certificates are checked, the specification validator must verify for
every registered definition:

- the LHS root is the declared first-class defined operator;
- LHS and RHS contain exactly the same schema metavariable set;
- repeated metavariables are consistent;
- the definition dependency graph is acyclic.

The current M0 definitions are:

```text
DEF_OR
DEF_STRICT_IMP
DEF_EQUIV_S
```

---

## 13. Surface identity and full erasure

Two distinct notions are deliberately separated.

### 13.1 Surface identity

This is the identity relation used by all Lewis primitive rules.

It compares the actual visible AST, including:

```text
or
strict_imp
equiv_s
```

as first-class nodes.

### 13.2 Full erasure

A deterministic diagnostic function recursively expands all three definitions
until only:

```text
atom
neg
and
poss
```

remain.

Full erasure is useful for:

- conservativity checks;
- specification validation;
- a fully expanded diagnostic renderer.

It is **not** used to make a failed `Sa`, `Sb`, `Ad`, or `Smp` application pass.

---

## 14. Primitive proof rendering versus erased formula rendering

`primitive-only proof` means:

- no derived theorem macro;
- no bridge macro;
- only `postulate_instance`, `Sa`, `Sb`, `Ad`, `Smp`, and explicit
  `definition_conversion`.

It does **not** mean that the fishhook or `equiv_s` must disappear.

A separate optional `fully erased formulas` diagnostic view may expand all
defined connectives into `neg/and/poss`.

This distinction preserves Lewis-style readable proofs while keeping the kernel
contract exact.

---

## 15. S5 basis discipline

Every S5 proof declares exactly one:

```text
S5_PRIMARY_B1_B7_C11
S5_ALT_B1_B7_C10_C12
```

Primitive schema admission is checked only against that basis.

The checker must never accept the union:

```text
B1-B7 + C10 + C11 + C12
```

as one basis.

A future bridge entry records both:

```yaml
source_basis_id: ...
target_basis_id: ...
```

and expands to a target-basis native certificate before kernel acceptance.

---

## 16. Future derived and bridge nodes

Search/library layers may use compact macros, but a compact macro is untrusted.

Before the kernel boundary it must expand to the normative certificate kinds in
this document.

No theorem cache, citation, historical theorem number, semantic validity test,
or declared system inclusion may bypass expansion and checking.

---

## 17. Certificate acceptance theorem-of-design

A future M1 checker conforms to M0 only if two independent implementations,
given the same `spec/*.yaml` and certificate, are forced by this contract to
agree on:

- the selected primitive basis;
- schema instantiation;
- object-level substitution;
- occurrence selection;
- definition conversion;
- adjunction;
- strict detachment;
- root/goal identity.

Any implementation-dependent implicit conversion is nonconforming.
