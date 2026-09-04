# Executable M0.3 Specification

The executable M0.3 candidate is:

```text
language.yaml
rules.yaml
schemas.yaml
systems.yaml
```

The trusted certificate boundary is jointly specified by:

```text
spec/rules.yaml
spec/systems.yaml
docs/PROOF_CERTIFICATE_SPEC.md
```

## Candidate invariants

- fishhook preserved;
- strict equivalence represented by `equiv_s`, never object-language `=`;
- no Box in M0;
- B9 excluded;
- no implicit definition conversion;
- exact surface-AST matching for Lewis primitive operations;
- `postulate_instance` separated from object-level `Sa`;
- one normative occurrence-path grammar;
- every proof declares `basis_id`;
- S5 primary and alternative bases remain separate.

## Validation

```bash
python scripts/validate_spec.py
python scripts/validate_source_register.py
python scripts/validate_spec.py --freeze
python scripts/validate_source_register.py --freeze
pytest
```

Passing these checks means the repository is structurally ready for the focused
independent closure audit. It does not itself certify M0.
