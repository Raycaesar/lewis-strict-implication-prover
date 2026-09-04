# System and Basis Bridges

This directory is reserved for machine-checked bridge proofs.

Priority bridges include:

1. reuse of S1 results inside S2;
2. S2-level principles reconstructed in the normalized S3 basis;
3. S3-level principles reconstructed in S4;
4. S4-level principles reconstructed in S5;
5. equivalence between the primary S5 basis `S1 + C11` and the alternative `S1 + C10 + C12` basis.

## Important invariant

A bridge is a proof object, not a configuration declaration.

Do not write:

```text
S3 inherits S2 axioms
```

unless the exact required principles are primitive in both normalized bases.

For non-literal basis inclusion, provide target-system certificates.
