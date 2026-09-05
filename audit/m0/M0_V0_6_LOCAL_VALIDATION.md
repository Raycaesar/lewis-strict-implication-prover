# M0.6 local release validation

Overall validator/test result: `PASS`
Collected tests: `44`

## Non-regression checks

- 12 schema ASTs unchanged from M0.5: `True`
- 3 definition ASTs unchanged from M0.5: `True`
- systems/bases/bridges unchanged except version/status metadata: `True`
- pre-existing canonical contract semantics unchanged: `True`
- M0.6 adds one `document_boundary` subtree: `True`
- independent whole-contract SHA-256 matches lock: `True`

Standalone source-register path checks used placeholder files at the exact registered literature paths.
Those placeholders are not included in the release package; the user's repository contains the real sources.

## `/opt/pyvenv/bin/python scripts/validate_spec.py`

Exit code: `0`

```text
M0 SPEC VALIDATION: PASS
  spec version: 0.6
  AST constructors: 7
  primitive schemas: 12
  Lewis operations: 4
  trusted certificate kinds: 6
  systems: 5
```

## `/opt/pyvenv/bin/python scripts/validate_source_register.py`

Exit code: `0`

```text
M0 SOURCE REGISTER VALIDATION: PASS
  register: audit/m0/source_register.yaml
  obligations: audit/m0/foundational_obligations.yaml
  primitive schemas: 12
  primitive operations: 4
  systems: 5
```

## `/opt/pyvenv/bin/python scripts/validate_spec.py --freeze`

Exit code: `0`

```text
M0 SPEC FREEZE READINESS: PASS
  spec version: 0.6
  AST constructors: 7
  primitive schemas: 12
  Lewis operations: 4
  trusted certificate kinds: 6
  systems: 5
```

## `/opt/pyvenv/bin/python scripts/validate_source_register.py --freeze`

Exit code: `0`

```text
M0 SOURCE REGISTER FREEZE READINESS: PASS
  register: audit/m0/source_register.yaml
  obligations: audit/m0/foundational_obligations.yaml
  primitive schemas: 12
  primitive operations: 4
  systems: 5
```

## `/opt/pyvenv/bin/python -m pytest -q`

Exit code: `0`

```text
[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                             [100%][0m
```

