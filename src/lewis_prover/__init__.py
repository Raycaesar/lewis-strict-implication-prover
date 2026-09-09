"""Trusted native syntactic infrastructure for the Lewis S1--S5 prover."""

from .kernel import FrozenSpec, load_frozen_spec, validate_frozen_spec

__all__ = ["FrozenSpec", "load_frozen_spec", "validate_frozen_spec"]
