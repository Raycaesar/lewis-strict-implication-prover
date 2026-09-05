# M0.6 freeze checklist

## Local candidate

- [ ] `python scripts/validate_spec.py`
- [ ] `python scripts/validate_source_register.py`
- [ ] `python scripts/validate_spec.py --freeze`
- [ ] `python scripts/validate_source_register.py --freeze`
- [ ] `pytest`
- [ ] `git ls-files '*:Zone.Identifier'` prints nothing
- [ ] exact-SHA GitHub Actions green

## M0.6 narrow repair

- [x] duplicate mapping/object keys rejected before mapping construction
- [x] policy stored inside the sole canonical contract
- [x] one trusted serialized format fixed: strict UTF-8 JSON object
- [x] duplicate detection recursive at every JSON object
- [x] nonstandard NaN/Infinity rejected
- [x] document conformance fixture added
- [x] duplicate root fixture added
- [x] duplicate nested justification fixture added
- [x] duplicate nested formula fixture added
- [x] canonical policy mutation fails freeze validation
- [x] whole-contract lock recomputed over contract v1.1
- [x] M0-C05 reopened pending independent recheck

## Independent closure

- [ ] exact candidate SHA inserted into M0.6 closure prompt
- [ ] focused Work Max recheck returns first line exactly:
  `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`

Only then perform the administrative frozen-status commit and begin M1.
