# Historical snapshot notice

This file records the **pre-audit / pre-M0.3 first-pass state**. It is retained for provenance and is not the current normative repair status.

For current status see:

- `M0_FOUNDATIONAL_AUDIT_2026-09-04.md`
- `M0_FOUNDATIONAL_REPAIR_LOG_v0.3.md`
- `foundational_obligations.yaml`

---

# M0 first-pass foundational source findings

**Status:** source pass before Work Max certification  
**Scope:** current `spec/*.yaml`, repository architecture, Lewis & Langford 1932,
Parry 1939, Feys, and modern cross-check material.

## Executive result

The current project direction is viable and the main normalized S1–S5 bases
are well supported by the sources. The structural validator and GitHub CI are
already functioning.

However, **M0 should not yet be frozen**. Three specification-level issues
should be resolved before the final foundational audit.

---

## 1. M0 blocker: `equiv_s` needs an explicit kernel-level status

Lewis & Langford p. 123 list logical equivalence among the primitive or
undefined ideas. On p. 124, 11.03 gives the relation

```text
p = q =df (p fishhook q)(q fishhook p)
```

and immediately comments that this definition does not simply remove the
primitive idea from the presentation.

Our project is right to reject object-language `=` and to use `equiv_s`.
The unresolved issue is different: **what exactly does the trusted kernel do
with `equiv_s`?**

Current M0 wording says the kernel *may* elaborate `equiv_s` to its definition.
That is too permissive for a trusted kernel.

### Recommended resolution

Use three levels:

1. **surface formula AST** — retains `strict_imp`, `or`, and `equiv_s`;
2. **metadefinition registry** — 11.01, 11.02, 11.03;
3. **explicit trusted definition conversion** — a certificate operation which
   verifies expansion/contraction at a specified occurrence.

Definition conversion is **not** a fifth Lewis inference rule. It is a
metalinguistic use of the definitions and should render as e.g. `Df 11.03`.

This permits historical proof lines such as:

```text
(A fishhook B)(B fishhook A)
A equiv_s B                      Df 11.03
```

without pretending that definition conversion is an additional axiom or
logical rule.

The final Work Max audit should actively test whether this architecture is
faithful and non-circular, especially because `Sb` itself is replacement of
strict equivalents.

---

## 2. M0 repair: Sa/Sb/Ad/Smp are project labels, not L&L symbolic labels

L&L pp. 125–126 give the operations under the headings:

- `Substitution` (a): replacement of equivalent expressions;
- `Substitution` (b): uniform substitution for proposition letters;
- `Adjunction`;
- `Inference`.

The convenient labels

```text
Sa
Sb
Ad
Smp
```

are our editorial/project labels (and agree with the notation used in the
associated manuscript), not literal labels printed by Lewis & Langford.

Therefore `rules.yaml` should use `project_label`, not `historical_label`.

Feys supplies a useful later cross-check:

- 30.21 substitution;
- 30.22 adjunction;
- 30.23 detachment for strict implication;
- 30.24 replacement of strict equivalents.

This repair changes no theorem set; it corrects provenance.

---

## 3. M0 repair: A1–A6 are not all literal B1–B6 duplicates

The current prose says, too strongly, that A1–A6 duplicate B1–B6
"formula-for-formula".

L&L Appendix II p. 493 shows otherwise. In particular, A2 and A4 are not
literal copies of B2 and B4.

This does **not** undermine the normalized prover basis.

Parry 1939, pp. 137–138, is especially useful here. Parry explicitly takes
S3 with:

```text
11.1–11.7 + 30.1
```

where 30.1 is the A8-style modal contraposition principle, and explains how the
emended Survey postulates A1–A8 are obtained. He also treats B1–7 or A1–7 as
presentations of S1.

So the correct project statement is:

> We do not store separate executable A1–A7 copies. The normalized S1 basis
> B1–B7 recovers the A-series principles required for the S3 presentation;
> A8 is the genuinely additional S3 schema stored by the prover.

That is a derivability/normalization claim, not a literal-text identity claim.

---

## 4. Source verification of the executable schemas

Direct visual comparison against L&L gives the following source locations:

| Project schema | L&L source |
| --- | --- |
| B1 | 11.1 p. 124; Appendix II p. 493 |
| B2–B7 | 11.2–11.7 p. 125; Appendix II p. 493 |
| B8 | Appendix II p. 493; Chapter VI 19.01 |
| A8 | Appendix II p. 493 |
| C10 | Appendix II p. 497 |
| C11 | Appendix II p. 497 |
| C12 | Appendix II p. 497 |

The current AST nestings for A8 and C10–C12 match the displayed native
diamond/negation forms on this pass. They should still be independently checked
again in Work Max because modal negation strings are especially vulnerable to
transcription error.

---

## 5. Source verification of S1–S5 bases

L&L Appendix II states:

- p. 500: S1 from B1–B7;
- p. 500: S2 from B1–B8;
- p. 500: historical S3 from A1–A8;
- p. 501: S4 from B1–B7 + C10;
- p. 501: S5 from B1–B7 + C11, or from B1–B7 + C10 + C12.

The project normalization

```text
S3 = S1 + A8
```

has direct secondary syntactic support in Parry 1939, pp. 137–138.

This is much stronger support than treating the normalized basis as an
implementation convenience invented by us.

---

## 6. Source verification of S5 bridge obligations

L&L p. 498 states:

- item (12): C10 is deducible from C11;
- item (13): C12 is deducible from C11;
- item (14): C11 is deducible from C10 and C12.

Page 499 summarizes the equivalence, and p. 501 uses the two bases in the
definition of S5.

Accordingly, our bridge queue is historically correct:

```text
C11 -> C10
C11 -> C12
C10 + C12 -> C11
```

The last is particularly suitable for the Shen Yuting historical regression.

These source statements are not substitutes for future kernel certificates.

---

## 7. No unrestricted necessitation

The current design remains correct in refusing to import unrestricted
necessitation into the native core.

The L&L Chapter VI operations on pp. 125–126 are substitution, adjunction, and
inference, including substitution of equivalents. There is no unrestricted
`A / Box A` rule in the chosen calculus.

Modern Hughes/Cresswell material independently emphasizes the failure of
unrestricted necessitation for S2 and S3.

---

## 8. Repository hygiene finding: Windows `Zone.Identifier`

The latest Git tree contains real files such as:

```text
scripts/validate_spec.py:Zone.Identifier
tests/spec/test_rule_spec.py:Zone.Identifier
.github/workflows/m0-spec-validation.yml:Zone.Identifier
```

They are Windows Mark-of-the-Web metadata materialized as ordinary files in
WSL/Git.

They do not affect theorem proving, but they should be removed and ignored.

Use the included:

```bash
bash scripts/clean_windows_metadata.sh
```

then commit the deletions.

For future ChatGPT ZIPs, prefer extracting with Linux `unzip` inside WSL rather
than Windows Explorer.

---

## 9. Work Max readiness

After the safe provenance/wording repairs in this package are merged and the
three definition/certificate blockers are explicitly resolved, the project is
at the correct point for its first Work Max foundational audit.

Do not start M1 trusted-kernel implementation before that verdict.
