# M0.5 freeze checklist

- [ ] exact candidate commit recorded
- [ ] `python scripts/validate_spec.py`
- [ ] `python scripts/validate_source_register.py`
- [ ] `python scripts/validate_spec.py --freeze`
- [ ] `python scripts/validate_source_register.py --freeze`
- [ ] `pytest`
- [ ] `git ls-files '*:Zone.Identifier'` empty
- [ ] exact-SHA GitHub Actions green
- [x] one machine-readable certificate authority only
- [x] legacy semantic registries removed
- [x] human certificate prose explicitly nonnormative
- [x] whole canonical contract fingerprinted
- [x] nine former false-positive mutations have direct rejection tests
- [x] legacy registry injection tests exist
- [ ] independent narrow P2 closure recheck returns
  `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`

Only then mark M0 frozen and begin M1.
