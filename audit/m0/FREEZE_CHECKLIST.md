# M0.6 freeze checklist

## Frozen M0.6

- [x] `python scripts/validate_spec.py`
- [x] `python scripts/validate_source_register.py`
- [x] `python scripts/validate_spec.py --freeze`
- [x] `python scripts/validate_source_register.py --freeze`
- [x] `pytest`
- [x] `git ls-files '*:Zone.Identifier'` prints nothing
- [x] exact-SHA GitHub Actions green

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
- [x] M0-C05 reopened and subsequently closed by independent recheck

## Independent closure

- [x] exact candidate SHA inserted into M0.6 closure prompt
- [x] focused Work Max recheck returns first line exactly:
  `M0 FOUNDATIONAL SPECIFICATION CERTIFIED`

The administrative frozen-status transition is complete. M1 may begin.
