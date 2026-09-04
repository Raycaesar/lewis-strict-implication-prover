# M0.4.1 integration hotfix

This hotfix does **not** change the M0.4 logical or certificate specification.

It fixes two local integration problems that can occur when the v0.4 ZIP is
extracted over an older repository:

1. ZIP overlay extraction does not delete superseded v0.3 test files, so old
   tests can remain and fail against the new M0.4 contract.
2. Ubuntu/WSL may expose `python3` but not a `python` command unless the local
   virtual environment is activated.

## Apply

From the repository root:

```bash
unzip -o LEWIS_M0_V0_4_1_INTEGRATION_HOTFIX.zip -d .
bash scripts/apply_m0_v0_4_cleanup.sh
bash scripts/run_m0_checks.sh
```

`run_m0_checks.sh` uses `.venv/bin/python` directly when available, so activation
is not required.

The cleanup removes only the six superseded v0.3 test modules:

```text
test_language_spec.py
test_rule_spec.py
test_schema_spec.py
test_source_register.py
test_system_spec.py
test_validator.py
```

Their M0.4 replacements remain under `tests/spec/`.
