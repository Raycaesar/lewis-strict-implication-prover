# Proof Library

This directory will contain checked proof certificates and certified derived macros.

Suggested future layout:

```text
proofs/
├── historical/
├── derived/
└── bridges/
```

## Rule

Nothing in this directory becomes trusted merely by being committed.

Every certificate must pass the trusted kernel.

A derived theorem should declare:

- theorem ID;
- formula;
- minimal claimed system;
- provenance;
- certificate path;
- primitive-only expansion status.
