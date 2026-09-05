# M0.4 local validation summary

Overall result: `PASS`

Collected pytest tests: `unknown`

The standalone release test used empty placeholder files at the exact registered historical-source paths. The user's repository contains the real source files; the placeholders are not included in the repair ZIP.

## `/opt/pyvenv/bin/python scripts/validate_spec.py`

Exit code: `0`

```text
M0 SPEC VALIDATION: PASS
  spec version: 0.4
  AST constructors: 7
  primitive schemas: 12
  primitive Lewis rules: 4
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
  spec version: 0.4
  AST constructors: 7
  primitive schemas: 12
  primitive Lewis rules: 4
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
[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                           [100%][0m
```

