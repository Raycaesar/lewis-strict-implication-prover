# Executable M0.4 Specification

The executable M0.4 candidate consists of:

```text
language.yaml
rules.yaml
schemas.yaml
systems.yaml
```

Key invariants:

- fishhook preserved;
- `equiv_s` distinct from metalanguage equality;
- no Box;
- no B9;
- no implicit definition conversion;
- exact surface-AST Lewis-rule matching;
- closed-world certificate serialization;
- `postulate_instance` distinct from `Sa`;
- one occurrence-path grammar;
- every proof has `basis_id`;
- S5 primary/alternative bases are separate;
- S5 bridges use operational `from_basis_id` / `into_basis_id`.

Run both normal and `--freeze` validators before the independent closure audit.
