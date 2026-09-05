# M0.5 local release validation

Overall: `PASS`
Collected tests: `32`

The standalone source-register path check used placeholder files at the exact
registered literature paths. The user's repository contains the real source files;
placeholders are not included in the repair package.

## `/opt/pyvenv/bin/python scripts/validate_spec.py`

Exit code: `0`

```text
M0 SPEC VALIDATION: PASS
  spec version: 0.5
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
  spec version: 0.5
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
[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                         [100%][0m
```

