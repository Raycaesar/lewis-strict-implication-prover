# Executable M0 Specification

The four YAML files in this directory are the executable specification for the
current M0 calculus:

```text
language.yaml
rules.yaml
schemas.yaml
systems.yaml
```

They are deliberately separated from prose documentation.

## Authority and trust

During M0, these files are **draft executable specifications**. They are not yet
frozen. A later foundational audit will compare them against Lewis & Langford
(1932) and the project's normalization policy.

After that audit, the project may create a lock/fingerprint for the frozen M0
specification. Until then, do not treat file hashes as mathematical evidence.

## What `scripts/validate_spec.py` checks

The validator checks structural and policy invariants, including:

- all four files exist and parse as YAML mappings;
- duplicate YAML keys are rejected;
- component/project/version metadata agree;
- AST operators referenced by schemas and definitions are registered;
- schema metavariables use explicit `{meta: ...}` nodes;
- no `box`, material implication, or object-language equality enters the M0 AST;
- `equiv_s` is distinct from metalanguage equality;
- the only primitive proof rules are `Sa`, `Sb`, `Ad`, and `Smp`;
- unrestricted necessitation remains disabled;
- the executable primitive schema registry contains exactly the normalized
  M0 set currently intended by the project;
- A1–A7 and B9 do not silently enter the primitive registry;
- all system-basis references resolve;
- system inheritance is acyclic;
- the normalized bases resolve to the intended S1–S5 schema sets;
- every S1–S5 basis uses exactly the four registered primitive rules;
- theorem inclusion is not trusted by the kernel without bridge certificates;
- the B9 extension remains disabled.

The validator intentionally **does not prove that the axiom formulas are
historically or mathematically correct**. That is a foundational source-audit
obligation, not something a structural validator can establish without
duplicating the calculus in code.

## Local use

From the repository root:

```bash
python -m pip install -e ".[dev]"
python scripts/validate_spec.py
pytest
```

The validator exits with code `0` on success and `1` on specification failure.

## CI

`.github/workflows/m0-spec-validation.yml` runs the validator and the M0 tests
on pushes and pull requests that touch the specification or validation
infrastructure.
