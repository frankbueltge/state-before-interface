import importlib.util
import json
import shutil
from pathlib import Path

from sentinel import gate
from sentinel.run import run

from .test_run import NOTICE, FakeClient, make_repo

REPO_ROOT = Path(__file__).parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_repo(tmp_path: Path) -> Path:
    root = make_repo(tmp_path)
    # verify + site generator live at the repo root and are exercised in place
    shutil.copytree(REPO_ROOT / "site", root / "site",
                    ignore=shutil.ignore_patterns("__pycache__"))
    (root / "site" / "config.json").write_text(json.dumps({"repo_url": ""}))
    run(root, "2026-08-01",
        FakeClient([NOTICE], {"https://ted.example/100-2026/xml": (b"<xml v1/>", 200)}))
    run(root, "2026-08-02",
        FakeClient([], {"https://ted.example/100-2026/xml": (b"<xml v2/>", 200)}))
    return root


def test_verify_criteria_stay_in_sync_with_gate():
    verify = _load("verify_sync", REPO_ROOT / "verify.py")
    assert verify.CRITERIA == gate.CRITERIA


def test_generated_page_and_chain_verify_clean(tmp_path):
    root = _fixture_repo(tmp_path)
    sitegen = _load("sitegen_t", root / "site" / "generate.py")
    sitegen.build(root)
    page = (root / "public" / "index.html").read_text()
    assert "no signal" not in page.split("Runs")[0]  # header untouched
    assert "DECLINED" in page or "CHANGED_NOTICE" in page

    verify = _load("verify_t", REPO_ROOT / "verify.py")
    assert verify.check(root) == []


def test_verify_finds_tampered_bytes_and_stale_page(tmp_path):
    root = _fixture_repo(tmp_path)
    sitegen = _load("sitegen_t2", root / "site" / "generate.py")
    sitegen.build(root)
    verify = _load("verify_t2", REPO_ROOT / "verify.py")
    assert verify.check(root) == []

    xml = root / "snapshots" / "2026-08-01" / "notices" / "100-2026.xml"
    xml.write_bytes(b"<xml tampered/>")
    problems = verify.check(root)
    assert any("do not match manifest sha256" in p for p in problems)

    xml.write_bytes(b"<xml v1/>")
    (root / "public" / "index.html").write_text("edited by hand")
    problems = verify.check(root)
    assert any("deterministic rebuild" in p for p in problems)
