"""Single system/basis lookup used by structural loading and logical checks."""

from lewis_prover.errors import CertificateBasisError

from .frozen_spec import validate_frozen_spec
from .model import FrozenBasis, FrozenSpec


def validate_basis(system: str, basis_id: str, frozen_spec: FrozenSpec) -> FrozenBasis:
    """Resolve one exact frozen basis, without aliases, unions, or bridges.

    The supplied spec and all derived basis data must match the authenticated
    M0 snapshot. Only that snapshot's basis may reach primitive admission.
    """
    frozen_spec = validate_frozen_spec(frozen_spec)
    if not isinstance(system, str) or not system or not isinstance(basis_id, str) or not basis_id:
        raise CertificateBasisError("certificate system and basis_id must be nonempty registered strings")
    basis = frozen_spec.bases.get(basis_id)
    if basis is None or basis.system_id != system:
        raise CertificateBasisError(f"unregistered system/basis_id pair: {system!r}/{basis_id!r}")
    return basis
