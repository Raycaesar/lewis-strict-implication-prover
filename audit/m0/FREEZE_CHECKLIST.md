# M0.4 freeze checklist

## Local checks

- [ ] `bash scripts/apply_m0_v0_4_cleanup.sh`
- [ ] `python scripts/validate_spec.py`
- [ ] `python scripts/validate_source_register.py`
- [ ] `python scripts/validate_spec.py --freeze`
- [ ] `python scripts/validate_source_register.py --freeze`
- [ ] `pytest`
- [ ] `git ls-files '*:Zone.Identifier'` prints nothing
- [ ] exact-SHA GitHub Actions is green

## Second closure repairs

- [x] certificate objects are closed-world
- [x] exact allowed fields per justification kind
- [x] node/root/parent IDs are nonempty strings with exact identity
- [x] S5 bridge fields renamed to from/into
- [x] primary→alternative C11 bridge orientation
- [x] alternative→primary C10/C12 bridge orientation
- [x] expanded certificate checks in into_basis_id
- [x] all active Parry fields use reduced-list/derived-11.5 wording
- [x] seven demonstrated freeze-gate false positives now rejected
- [x] repair-log parent vocabulary corrected
- [x] fingerprint metadata validated
- [x] post-certification `closed` status transition supported

## Independent closure

- [ ] insert exact new candidate SHA into the closure prompt
- [ ] run focused Work Max recheck
- [ ] no P0/P1 remains
- [ ] no freeze-undermining P2 remains
- [ ] first line is exactly:
  `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`

Only then mark M0 frozen and start M1.
