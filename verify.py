#!/usr/bin/env python3
"""Walk the provenance chain backwards and fail on any hole (invariant I1).

public form → claim → evidence → preserved bytes → manifest (URL, UTC time,
SHA-256). Also enforces: candidate verdicts consistent with their criteria,
case states legal, autonomy protocol present for every run, and public/
byte-identical to a fresh deterministic rebuild.

Stdlib only. Exit code 1 lists every hole found.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

CRITERIA = (
    "observable_public_problem",
    "machine_readable_evidence",
    "consequential_relation",
    "machine_scale_advantage",
    "falsifiable_investigation",
    "digital_form_possible",
)

VALID_STATES = {
    "CASE_OPEN", "INVESTIGATING",
    "FALSE_ALARM", "INSUFFICIENT_EVIDENCE", "INTERESTING_BUT_TRIVIAL",
    "RESEARCH_RESULT", "PUBLIC_WORK", "ONGOING_OBSERVATORY",
}

MANIFEST_KEYS = ("file", "url", "retrieved_at", "http_status", "sha256")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _check_manifest(root: Path, manifest_path: Path, registry: dict,
                    problems: list[str]) -> None:
    manifest = load(manifest_path)
    for entry in manifest.get("entries", []):
        missing = [k for k in MANIFEST_KEYS if k not in entry]
        if missing:
            problems.append(f"{manifest_path}: entry missing {missing}")
            continue
        target = root / entry["file"]
        if not target.exists():
            problems.append(f"{entry['file']}: listed in manifest but missing")
        elif sha256_file(target) != entry["sha256"]:
            problems.append(f"{entry['file']}: bytes do not match manifest sha256")
        else:
            registry[entry["file"]] = entry


def check(root: Path) -> list[str]:
    problems: list[str] = []
    registry: dict[str, dict] = {}

    snapdir = root / "snapshots"
    day_dirs = sorted(d for d in snapdir.iterdir() if d.is_dir()) \
        if snapdir.exists() else []
    for day_dir in day_dirs:
        manifest_path = day_dir / "manifest.json"
        if not manifest_path.exists():
            problems.append(f"{day_dir.name}: missing manifest.json")
            continue
        _check_manifest(root, manifest_path, registry, problems)
        if not (day_dir / "run.json").exists():
            problems.append(f"{day_dir.name}: missing run.json")
        listed = {e["file"] for e in load(manifest_path).get("entries", [])}
        for file in day_dir.rglob("*"):
            if file.is_file() and file.name not in ("manifest.json", "run.json"):
                rel = file.relative_to(root).as_posix()
                if rel not in listed:
                    problems.append(f"{rel}: preserved but not manifested")

    for evidence_manifest in sorted(root.glob("cases/*/evidence/manifest.json")):
        _check_manifest(root, evidence_manifest, registry, problems)

    index_path = snapdir / "index.json"
    index = load(index_path) if index_path.exists() else {"notices": {}}
    for pubnum, entry in sorted(index["notices"].items()):
        if not entry.get("versions"):
            problems.append(f"index {pubnum}: no preserved version")
        for version in entry.get("versions", []):
            manifested = registry.get(version["file"])
            if manifested is None:
                problems.append(f"index {pubnum}: {version['file']} not manifested")
            elif manifested["sha256"] != version["sha256"]:
                problems.append(f"index {pubnum}: sha mismatch vs manifest")

    open_ids: set[str] = set()
    for candidate_file in sorted(root.glob("candidates/*.json")):
        candidate = load(candidate_file)
        cid = candidate.get("id", candidate_file.stem)
        if set(candidate.get("criteria", {})) != set(CRITERIA):
            problems.append(f"{cid}: criteria set differs from the six-criteria gate")
            continue
        for name, verdict in candidate["criteria"].items():
            if not verdict.get("reason"):
                problems.append(f"{cid}: criterion {name} has no reason")
        all_pass = all(v["passed"] for v in candidate["criteria"].values())
        if (candidate.get("verdict") == "OPEN") != all_pass:
            problems.append(f"{cid}: verdict inconsistent with criteria")
        for pubnum in candidate.get("signal", {}).get("notices", []):
            if pubnum not in index["notices"]:
                problems.append(f"{cid}: references unknown notice {pubnum}")
        if candidate.get("verdict") == "OPEN":
            open_ids.add(cid)

    case_ids: set[str] = set()
    for state_file in sorted(root.glob("cases/*/state.json")):
        cid = state_file.parent.name
        case_ids.add(cid)
        state = load(state_file)
        if state.get("state") not in VALID_STATES:
            problems.append(f"{cid}: illegal state {state.get('state')!r}")
        if not state.get("history"):
            problems.append(f"{cid}: empty state history")
        if not (state_file.parent / "log.jsonl").exists():
            problems.append(f"{cid}: missing autonomy log.jsonl")
        claims_file = state_file.parent / "claims.json"
        if claims_file.exists():
            for claim in load(claims_file).get("claims", []):
                if not claim.get("evidence"):
                    problems.append(f"{cid} claim {claim.get('id')}: no evidence refs")
                for ref in claim.get("evidence", []):
                    if ref not in registry:
                        problems.append(
                            f"{cid} claim {claim.get('id')}: evidence {ref} "
                            "is not preserved-and-manifested")
    if open_ids != case_ids:
        problems.append(f"OPEN candidates {sorted(open_ids)} do not match "
                        f"case directories {sorted(case_ids)}")

    log_path = root / "autonomy" / "log.jsonl"
    run_dates = {load(p)["date"] for p in root.glob("snapshots/*/run.json")}
    logged = set()
    if log_path.exists():
        for i, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                problems.append(f"autonomy log line {i}: unparseable")
                continue
            if entry.get("step") == "sentinel-run":
                logged.add(entry.get("detail", {}).get("date"))
    for missing_date in sorted(run_dates - logged):
        problems.append(f"run {missing_date} has no autonomy protocol entry")

    generator = root / "site" / "generate.py"
    public = root / "public"
    if generator.exists():
        spec = importlib.util.spec_from_file_location("sitegen", generator)
        sitegen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sitegen)
        with tempfile.TemporaryDirectory() as tmp:
            fresh = sitegen.build(root, Path(tmp) / "public")
            fresh_files = {p.relative_to(fresh).as_posix(): p.read_bytes()
                           for p in fresh.rglob("*") if p.is_file()}
            public_files = {p.relative_to(public).as_posix(): p.read_bytes()
                            for p in public.rglob("*") if p.is_file()} \
                if public.exists() else {}
            if not public_files:
                problems.append("public/ missing — page not generated")
            elif fresh_files != public_files:
                changed = sorted(set(fresh_files) ^ set(public_files)) or sorted(
                    k for k in fresh_files
                    if fresh_files[k] != public_files.get(k))
                problems.append("public/ is not a deterministic rebuild of the "
                                f"committed records (differs: {changed[:5]})")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", type=Path)
    args = parser.parse_args(argv)
    problems = check(args.repo_root.resolve())
    if problems:
        print(f"provenance chain has {len(problems)} hole(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("provenance chain intact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
