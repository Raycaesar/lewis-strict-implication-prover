"""Minimal verifier-only frontend; all acceptance belongs to the kernel.

Verification writes one status line followed by a JSON detail object to stdout.
Exit 0 means accepted, 1 means rejected certificate, and 2 means verification
could not run (help, usage, file, frozen-spec, or internal error). Even --help
is nonzero: exit 0 is reserved for actual acceptance. No rendering or search
runs here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .errors import CertificateValidationError, FrozenSpecError
from .kernel import check_certificate, load_frozen_spec


class _UsageError(ValueError):
    pass


class _HelpRequested(ValueError):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _UsageError(message)

    def print_help(self, file=None) -> None:
        raise _HelpRequested(self.format_help())


def _result(status: str, detail: dict) -> None:
    print(status)
    print(json.dumps(detail, sort_keys=True, ensure_ascii=True))


def main(argv: list[str] | None = None) -> int:
    """Verify canonical bytes against the frozen bundle at --spec-root (cwd)."""
    parser = _Parser(prog="python -m lewis_prover", allow_abbrev=False)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="check a canonical JSON certificate", allow_abbrev=False)
    verify.add_argument("certificate", type=Path)
    verify.add_argument("--spec-root", type=Path, default=Path("."),
                        help="directory containing frozen spec/ and audit/m0/ (default: current directory)")
    try:
        args = parser.parse_args(argv)
        # Authenticate the basis first; never fall back to another directory,
        # cached candidate, permissive JSON parser, or renderer-based check.
        frozen = load_frozen_spec(args.spec_root)
        checked = check_certificate(args.certificate.read_bytes(), frozen)
    except _HelpRequested as exc:
        _result("INVALID_CERTIFICATE", {
            "code": "help_requested", "reason": "no certificate was verified", "help": str(exc),
        })
        return 2
    except _UsageError as exc:
        _result("INVALID_CERTIFICATE", {"code": "usage_error", "reason": str(exc)})
        return 2
    except FrozenSpecError as exc:
        _result("INVALID_CERTIFICATE", {
            "code": "frozen_spec_error", "detail_code": type(exc).__name__, "reason": str(exc),
        })
        return 2
    except OSError as exc:
        _result("INVALID_CERTIFICATE", {
            "code": "certificate_io_error", "detail_code": type(exc).__name__, "reason": str(exc),
        })
        return 2
    except CertificateValidationError as exc:
        _result("INVALID_CERTIFICATE", {
            "code": exc.code, "detail_code": exc.detail_code, "kind": exc.kind,
            "node_id": exc.node_id, "reason": exc.reason, "related_ids": exc.related_ids,
        })
        return 1
    except Exception as exc:
        # A frontend failure must never emit a valid status. Preserve an error
        # type for diagnosis without passing arbitrary exception text through.
        _result("INVALID_CERTIFICATE", {
            "code": "internal_error", "detail_code": type(exc).__name__,
            "reason": "verification could not complete",
        })
        return 2

    certificate = checked.certificate
    _result("VALID_CERTIFICATE", {
        "proof_id": certificate.proof_id, "system": certificate.system,
        "basis_id": certificate.basis_id, "root": certificate.root,
        "node_count": len(certificate.nodes),
    })
    return 0
