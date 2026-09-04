# Historical Regression Tests

This directory will contain theorem-level tests based on historically attested Lewis-system derivations.

The purpose is twofold:

1. verify that the normalized calculus reproduces intended historical theorems;
2. catch regressions in the trusted kernel.

## Initial test queue

### S1

- reflexive strict implication;
- the formula historically labelled A7, reconstructed as an S1 theorem;
- at least one multi-step theorem using substitution, adjunction, and strict detachment;
- replacement-of-equivalents example once `equiv_s` handling is frozen.

### S2

- theorem whose proof genuinely requires the B8 extension relative to the selected proof route.

### S3

- theorem/proof using A8.

### S4

- theorem/proof using C10.

### S5

- theorem/proof using C11;
- C10/C12/C11 bridge regression associated with the Shen material.

## Every positive test should have adversarial variants

Examples:

- wrong substitution map;
- non-uniform substitution;
- wrong schema label;
- use of B8 in S1;
- use of A8 in S2;
- malformed strict-detachment antecedent;
- replacement at the wrong path;
- replacement without an `equiv_s` premise;
- cyclic proof-DAG dependency.

A trusted checker is only useful if these are rejected.
