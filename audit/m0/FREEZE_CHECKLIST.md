# M0.3 freeze checklist

## Local candidate checks

- [ ] `python scripts/validate_spec.py`
- [ ] `python scripts/validate_source_register.py`
- [ ] `python scripts/validate_spec.py --freeze`
- [ ] `python scripts/validate_source_register.py --freeze`
- [ ] `pytest`
- [ ] `git ls-files '*:Zone.Identifier'` prints nothing
- [ ] GitHub Actions green on exact candidate commit

## Foundational repairs

- [x] explicit deterministic definition conversion
- [x] exact surface-AST primitive-rule matching
- [x] postulate/schema instantiation separated from Sa
- [x] Sa simultaneous one-pass nonrecursive semantics
- [x] one occurrence-path grammar
- [x] stable proof `basis_id`
- [x] separate S5 primary/alternative bases
- [x] source provenance corrected
- [x] audited formula ASTs regression-locked

## Independent closure

- [ ] exact candidate commit inserted into closure recheck prompt
- [ ] focused Work Max closure recheck executed
- [ ] no P0/P1 remains
- [ ] first-line verdict:
  `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`

Only then:

```text
M0 FROZEN
```

and M1 may begin.
