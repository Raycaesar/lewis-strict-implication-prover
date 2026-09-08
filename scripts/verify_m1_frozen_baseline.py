"""Reproduce M1's frozen-input provenance and M0 non-regression evidence.

Validation tooling only; production load_frozen_spec never shells out to Git.
Requires the recorded Git objects (CI checks out full history).
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import yaml

from lewis_prover.kernel import load_frozen_spec
from lewis_prover.kernel.frozen_baseline import (
    ADMINISTRATIVE_FREEZE_COMMIT, CERTIFIED_M0_COMMIT, FROZEN_INPUT_SHA256,
)


ROOT = Path(__file__).resolve().parents[1]
FAILED_M1_COMMIT = "e0837632aa9e187ccbc5a6fcc1a3a8816e17fe56"
REPLAY_COMMIT = "d87f1145da766f4ccbb7a9f9b76e9d15328d50da"
EVIDENCE = ROOT / "audit/m1/FROZEN_M0_NONREGRESSION.json"
ADMINISTRATIVE_PATHS = {
    "AGENTS.md", "PACKAGE_MANIFEST.txt", "README.md", "audit/m0/FREEZE_CHECKLIST.md",
    "audit/m0/foundational_obligations.yaml", "audit/m0/source_register.yaml",
    "audit/m0/M0_FOUNDATIONAL_M0_6_DUPLICATE_KEY_CLOSURE_RECHECK_2026-09-05.md",
    "docs/ARCHITECTURE.md", "docs/FOUNDATIONAL_SPEC_v0.6.md", "docs/ROADMAP.md",
    "spec/language.yaml", "spec/rules.yaml", "spec/schemas.yaml", "spec/systems.yaml",
}


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def protected_objects(raw):
    documents = {path: yaml.safe_load(data) for path, data in raw.items()}
    language, rules, schemas, systems = (documents[f"spec/{name}.yaml"] for name in ("language", "rules", "schemas", "systems"))
    objects = {
        f"{path}#excluding_root_status": {key: value for key, value in document.items() if key != "status"}
        for path, document in documents.items() if path.startswith("spec/")
    }
    objects.update({f"formula_ast.{key}": value for key, value in language["formula_ast"].items()})
    objects.update({f"schema.{key}": value["ast"] for key, value in schemas["schemas"].items()})
    objects.update({f"definition.{key}": {"lhs": value["lhs"], "rhs": value["rhs"]}
                    for key, value in language["metadefinitions"].items()})
    objects.update({f"basis.{system}.{key}": value
                    for system, entry in systems["systems"].items()
                    for key, value in entry.items() if key.endswith("normalized_basis")})
    objects["S5.bridge_obligations"] = systems["systems"]["S5"]["bridge_obligations"]
    objects["canonical_certificate_contract"] = rules["canonical_certificate_contract"]
    objects.update({path: value for path, value in documents.items() if path.startswith("audit/m0/")})
    return objects


def verify():
    require(git("rev-parse", ADMINISTRATIVE_FREEZE_COMMIT + "^").decode().strip() == CERTIFIED_M0_COMMIT,
            "Administrative freeze is not directly on the certified candidate")
    require(git("rev-parse", REPLAY_COMMIT + "^").decode().strip() == ADMINISTRATIVE_FREEZE_COMMIT,
            "M1 replay is not directly on the administrative freeze")
    require(git("rev-parse", REPLAY_COMMIT + "^{tree}") == git("rev-parse", FAILED_M1_COMMIT + "^{tree}"),
            "M1 replay tree differs from the audited failed implementation")
    changed = set(git("diff", "--name-only", CERTIFIED_M0_COMMIT, ADMINISTRATIVE_FREEZE_COMMIT).decode().splitlines())
    require(changed == ADMINISTRATIVE_PATHS, "Unexpected administrative freeze file changes")
    for path in sorted(changed):
        require(git("show", f"{ADMINISTRATIVE_FREEZE_COMMIT}:{path}") == git("show", f"{FAILED_M1_COMMIT}:{path}"),
                f"Administrative changes differ from the previously authorized transition: {path}")
    freeze_paths = git("ls-tree", "-r", "--name-only", ADMINISTRATIVE_FREEZE_COMMIT).decode().splitlines()
    require(not any(path.startswith(("src/lewis_prover/", "tests/kernel/", "tests/m1/", "tests/syntax/", "audit/m1/"))
                    for path in freeze_paths), "Administrative freeze contains M1 files")

    identities = {
        "certified_m0": CERTIFIED_M0_COMMIT, "administrative_freeze": ADMINISTRATIVE_FREEZE_COMMIT,
        "failed_m1_before_repair": FAILED_M1_COMMIT, "m1_replay": REPLAY_COMMIT,
    }
    snapshots = {label: {path: git("show", f"{revision}:{path}") for path in FROZEN_INPUT_SHA256}
                 for label, revision in identities.items()}
    snapshots["current"] = {path: (ROOT / path).read_bytes() for path in FROZEN_INPUT_SHA256}
    for label, raw in snapshots.items():
        if label != "certified_m0":
            for path, digest in FROZEN_INPUT_SHA256.items():
                require(sha256(raw[path]) == digest, f"Manifest mismatch at {label}:{path}")
        for path in FROZEN_INPUT_SHA256:
            if path.startswith("spec/"):
                expected = "candidate_m0" if label == "certified_m0" else "frozen_m0"
                require(yaml.safe_load(raw[path])["status"] == expected, f"Unexpected status at {label}:{path}")

    original = protected_objects(snapshots["certified_m0"])
    for label, raw in snapshots.items():
        require(protected_objects(raw) == original, f"Frozen M0 parsed objects changed at {label}")
    load_frozen_spec(ROOT)  # Raw identities and all existing production semantic defenses.
    return {
        "identities": identities,
        "administrative_files_only": sorted(changed),
        "replay_tree_equals_failed_m1": git("rev-parse", REPLAY_COMMIT + "^{tree}").decode().strip(),
        "input_file_sha256": {path: {label: sha256(raw[path]) for label, raw in snapshots.items()}
                              for path in FROZEN_INPUT_SHA256},
        "parsed_objects_equal_at": list(snapshots),
        "parsed_object_count": len(original),
        "parsed_object_sha256": {key: sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode())
                                 for key, value in sorted(original.items())},
        "comparison_policy": "Complete parsed spec documents differ only in root status between certified candidate and administrative freeze; all other protected objects equal. Six raw input files equal from freeze through current repair.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-evidence", action="store_true", help="write the verified deterministic audit record")
    args = parser.parse_args()
    evidence = verify()
    if args.write_evidence:
        EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        require(json.loads(EVIDENCE.read_bytes()) == evidence, "Stored non-regression evidence differs from recomputed evidence")
    print("PASS: 6 complete frozen input blobs match the administrative Git baseline")
    print(f"PASS: {evidence['parsed_object_count']} protected parsed M0 objects equal at certified M0, freeze, failed M1, replay, and current repair")
    print("PASS: pure administrative parent, exact M1 replay tree, and production integrity/semantic checks")


if __name__ == "__main__":
    main()
