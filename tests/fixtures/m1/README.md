# M1 kernel regression certificates

These six small, complete JSON certificates exercise the root justification
named by each filename: `postulate_instance`, `Sa`, `Sb`, `Ad`, `Smp`, and
`definition_conversion`. They are synthetic kernel regression fixtures, not
claims about historically interesting Lewis theorems or an M2 theorem corpus.

All fixtures declare exactly `S1_B1_B7`. The `Sa` fixture uses the simultaneous
map `p -> q, q -> r`. The `Sb` fixture obtains a surface equivalence by explicit
adjunction and definition contraction before replacing one occurrence.
Tests in `tests/m1/` mutate fresh copies or serialized bytes; the checked-in
fixtures and frozen M0 files are not changed by the tests.

## Verifier CLI

From the repository root, without requiring an editable package installation:

```bash
PYTHONPATH=src .venv/bin/python -m lewis_prover verify tests/fixtures/m1/Sb.json
```

After installation, `python -m lewis_prover verify <certificate.json>` is the
equivalent entry point. `--spec-root <directory>` explicitly selects the
directory containing frozen `spec/` and `audit/m0/`; the default is the current
directory, with no fallback to another specification bundle.

Verification emits exactly two stdout lines: `VALID_CERTIFICATE` or
`INVALID_CERTIFICATE`, then a JSON detail object with sorted keys. Rejections
include the checker's stable `code`, `detail_code`, `node_id`, `kind`, `reason`,
and `related_ids`. Exit 0 means accepted; exit 1 means a rejected certificate;
exit 2 means verification could not run (help, usage, frozen basis, I/O, or
internal error). `--help` returns its help text in the JSON detail and exits 2,
so no invocation can signal acceptance merely by requesting help.
There is no `prove` command.

## M1 audit-repair negative fixtures

`invalid/definition_conversion_skipped_reverse.json` contains a valid B5
instance adjoined to itself, followed by an invalid `DEF_EQUIV_S` contraction:
the second implication is not the required reverse implication. With the
ordinary frozen spec the CLI rejects this at definition conversion (exit 1).
The audited M1 loader falsely admitted it after a temporary spec changed
`formula_ast.and.fields` to `[left]`. The repaired loader rejects that spec
before certificate reading or theorem checking (exit 2).

`invalid/duplicate_members.json` rejects at the strict JSON document boundary
(exit 1). Run `python scripts/run_m1_cli_smoke.py` to check all six positive
fixtures, both negative fixtures, and the P0 temporary-spec mutation through
the production CLI.

## Reproducing validation and coverage

```bash
bash scripts/run_m0_checks.sh
.venv/bin/python -m pytest tests/m1
git diff --check
```

The first command includes every M0 and M1 test, including CLI subprocess smoke
tests. With the optional `coverage` test tool installed:

```bash
.venv/bin/python -m coverage run --branch --source=lewis_prover.kernel -m pytest
.venv/bin/python -m coverage report -m
```

Coverage is diagnostic, not an acceptance criterion. Input mutations must fail
at the intended layer, rather than merely failing for any unrelated reason.
