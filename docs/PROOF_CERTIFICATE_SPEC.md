# Proof Certificate Specification
## Provisional v0.1

This document specifies the shape of proof certificates expected by the future trusted kernel. It is intentionally conservative and may be tightened during M1.

## 1. Core principle

A proof certificate is data sufficient for the checker to verify the derivation without performing theorem search.

The checker may perform:

- structural matching;
- substitution validation;
- path lookup;
- exact rule validation.

It must not need to infer an omitted lemma or guess which rule was intended.

---

## 2. Proof as DAG

A proof certificate consists of:

```text
proof_id
system
goal
nodes
root
```

Each node has a stable node identifier.

Example shape:

```yaml
proof_id: example
system: S1
goal: ...
root: n7

nodes:
  n1:
    conclusion: ...
    justification:
      kind: axiom
      schema: B1
      substitution: ...

  n2:
    conclusion: ...
    justification:
      kind: rule
      rule: Sa
      parents: [n1]
      substitution: ...

  n7:
    conclusion: ...
    justification:
      kind: rule
      rule: Smp
      parents: [n5, n6]
```

The exact serialization format may later be JSON or YAML. Logical meaning must not depend on serialization.

---

## 3. Axiom-schema node

Required fields:

```text
kind = axiom
schema
conclusion
schema_substitution
```

The checker must independently verify that applying the recorded schema substitution to the schema AST yields the conclusion.

The schema must be primitive in the selected system, unless the node is explicitly a checked theorem-library invocation that expands further.

---

## 4. Uniform substitution (`Sa`)

A substitution step records:

- parent node;
- complete substitution map for metavariables/object proposition letters as specified;
- resulting conclusion.

Uniformity must be checked structurally.

Capture issues do not arise in the initial propositional core, but the representation must not assume this remains true if later quantified extensions are added.

---

## 5. Replacement of strict equivalents (`Sb`)

A replacement step must record:

```text
equivalence_parent
target_parent
direction
occurrence_path
conclusion
```

The equivalence parent must establish an object-language formula of the form:

```text
equiv_s(A, B)
```

The direction is one of:

```text
left_to_right
right_to_left
```

The occurrence path identifies exactly one occurrence in the target formula.

The checker must verify:

1. the path exists;
2. the subformula at that path is structurally identical to the source side;
3. replacement at exactly that path yields the declared conclusion.

A later extension may permit multiple simultaneous occurrences, but M1 should begin with one explicit occurrence per rule application.

---

## 6. Adjunction (`Ad`)

From checked parents concluding `A` and `B`, conclude the conjunction/product `A & B` in the normalized AST form.

No hidden commutativity or reassociation is allowed.

---

## 7. Strict detachment (`Smp`)

From checked parents:

```text
A
strict_imp(A, B)
```

conclude:

```text
B
```

The checker must require exact structural identity of the detached antecedent after any earlier explicit substitutions/replacements.

---

## 8. Derived theorem/macro node

A concise proof may contain:

```text
kind: derived
theorem_id: ...
parents: ...
```

but such a node is not trusted directly.

It must reference:

- a stored expansion;
- declared required system;
- exact instantiation;
- a kernel-checkable expanded certificate.

Primitive-only rendering recursively expands all such nodes.

---

## 9. Bridge node

System bridges are treated similarly to derived macros.

A theorem proved in another Lewis system may not be imported merely because theorem inclusion is mathematically known.

The import must reference a certified target-system bridge.

---

## 10. Provenance

Stored library proofs should carry:

```text
source_type
source_work
source_year
source_location
historical_label
notes
```

Provenance is not part of proof validity, but it is part of the research integrity of the library.

---

## 11. Linearization

The user-visible Hilbert proof is generated from the DAG by a deterministic topological ordering.

Every printed line contains:

1. line number;
2. rendered formula;
3. justification;
4. parent line numbers where applicable.

Example style:

```text
1. ...                              B1
2. ...                              Sa 1 [p := ..., q := ...]
3. ...                              Ad 1,2
4. ...                              Smp 3, ...
```

For `Sb`, the renderer should show the equivalence line, target line, direction, and optionally a human-readable occurrence description.

---

## 12. Verification invariant

A certificate is accepted iff every node is accepted in dependency order and the `root` node is structurally identical to the declared `goal`.

No separate "trusted theorem cache" may bypass this condition.


---

## 13. Definition conversion — M0 freeze issue

Historical proofs routinely move between a defined notation and its defining
expression. For this project, that includes `or`, the strict-implication
fishhook, and `equiv_s`.

This is **not** to become a fifth primitive Lewis inference rule.

The current candidate design is a trusted metalinguistic certificate node:

```yaml
kind: definition_conversion
parent: n12
definition_id: DEF_EQUIV_S
direction: contract
occurrence_path: []
conclusion: ...
```

The checker would verify that the selected occurrence is exactly the left- or
right-hand side of the registered metadefinition and that the declared
replacement yields the conclusion.

Whether this exact design is frozen must be decided in the M0 foundational
audit, especially because `equiv_s` is also the premise connective governing
`Sb`.

Until that decision is closed, M1 must not implement a permanent certificate
format for definition conversion.
