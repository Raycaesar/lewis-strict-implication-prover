# M0.3 local validation summary

This package was self-tested before handoff.

## `/opt/pyvenv/bin/python scripts/validate_spec.py`

Exit code: `0`

```text
M0 SPEC VALIDATION: PASS
  spec directory: spec
  spec version: 0.3
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
  spec directory: spec
  spec version: 0.3
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
[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m.[0m[32m                                      [100%][0m
```

Overall local result: `PASS`

For the source-register path checks, the standalone package self-test used placeholder files at the exact registered paths; the user's repository already contains the real literature files.
