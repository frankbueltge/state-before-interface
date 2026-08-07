import json
from pathlib import Path

import pytest

from sentinel.preserve import read_json, sha256, write_json
from sentinel.run import run


class FakeClient:
    """Implements the TedClient surface used by run()."""

    def __init__(self, search_hits, documents):
        self._hits = search_hits            # list of raw notice dicts
        self._documents = documents         # url -> (bytes, status)
        self.requests = 0
        self.http_429 = 0

    def search_all(self, query, fields, max_pages=10):
        self.requests += 1
        raw = json.dumps({"notices": self._hits,
                          "totalNoticeCount": len(self._hits)}).encode()
        return list(self._hits), len(self._hits), False, [raw]

    def fetch_document(self, url):
        self.requests += 1
        return self._documents[url]


def make_repo(tmp_path: Path) -> Path:
    write_json(tmp_path / "envelope" / "queries.json", {
        "version": 1, "as_of": "2026-08-01",
        "phrases": [{"lang": "eng", "text": "artificial intelligence"}],
        "lookback_days": 3, "change_window_days": 14, "pattern_window_days": 90,
    })
    return tmp_path


NOTICE = {
    "publication-number": "100-2026",
    "publication-date": "2026-08-01+02:00",
    "notice-title": {"eng": "Norway – Arbitrary waveform generator"},
    "buyer-name": {"eng": ["Some Lab"]},
    "buyer-country": ["NOR"],
    "classification-cpv": ["34999100"],
    "links": {"xml": {"MUL": "https://ted.example/100-2026/xml"}},
    "contact-name": "Jane Doe",
}


def test_first_run_preserves_and_declines_bycatch(tmp_path):
    root = make_repo(tmp_path)
    client = FakeClient([NOTICE], {"https://ted.example/100-2026/xml": (b"<xml v1/>", 200)})
    summary = run(root, "2026-08-01", client)

    xml = root / "snapshots" / "2026-08-01" / "notices" / "100-2026.xml"
    assert xml.read_bytes() == b"<xml v1/>"
    manifest = read_json(root / "snapshots" / "2026-08-01" / "manifest.json")
    files = {e["file"]: e for e in manifest["entries"]}
    assert files["snapshots/2026-08-01/notices/100-2026.xml"]["sha256"] == \
        sha256(b"<xml v1/>")

    index = read_json(root / "snapshots" / "index.json")
    assert "100-2026" in index["notices"]
    # I8: nothing person-shaped in derived data
    assert "Jane Doe" not in json.dumps(index)

    assert summary["opened"] == []
    assert len(summary["declined"]) == 1
    candidate = read_json(root / "candidates" / f"{summary['declined'][0]}.json")
    assert candidate["verdict"] == "DECLINED"

    run_record = read_json(root / "snapshots" / "2026-08-01" / "run.json")
    assert run_record["new_matches"] == ["100-2026"]
    log = (root / "autonomy" / "log.jsonl").read_text().strip().splitlines()
    assert json.loads(log[-1])["step"] == "sentinel-run"


def test_second_run_detects_change_and_no_duplicate_signals(tmp_path):
    root = make_repo(tmp_path)
    run(root, "2026-08-01",
        FakeClient([NOTICE], {"https://ted.example/100-2026/xml": (b"<xml v1/>", 200)}))
    summary = run(root, "2026-08-02",
                  FakeClient([], {"https://ted.example/100-2026/xml": (b"<xml v2/>", 200)}))

    assert summary["signals"] == 1
    index = read_json(root / "snapshots" / "index.json")
    assert len(index["notices"]["100-2026"]["versions"]) == 2
    kinds = {s["type"] for s in
             read_json(root / "snapshots" / "2026-08-02" / "run.json")["signals"]}
    assert kinds == {"CHANGED_NOTICE"}

    # third run: unchanged bytes, no new signal
    summary = run(root, "2026-08-03",
                  FakeClient([], {"https://ted.example/100-2026/xml": (b"<xml v2/>", 200)}))
    assert summary["signals"] == 0


def test_disappearance_marks_gone_and_same_day_rerun_is_refused(tmp_path):
    root = make_repo(tmp_path)
    run(root, "2026-08-01",
        FakeClient([NOTICE], {"https://ted.example/100-2026/xml": (b"<xml v1/>", 200)}))
    summary = run(root, "2026-08-02",
                  FakeClient([], {"https://ted.example/100-2026/xml": (b"", 404)}))
    kinds = {s["type"] for s in
             read_json(root / "snapshots" / "2026-08-02" / "run.json")["signals"]}
    assert kinds == {"DISAPPEARED"}
    assert read_json(root / "snapshots" / "index.json")["notices"]["100-2026"]["gone"]

    with pytest.raises(SystemExit):
        run(root, "2026-08-02", FakeClient([], {}))


def test_source_outage_is_recorded_not_bridged(tmp_path):
    from sentinel.fetch import SourceUnavailable

    class OutageClient(FakeClient):
        def search_all(self, query, fields, max_pages=10):
            self.requests += 1
            raise SourceUnavailable("https://api.ted.europa.eu/v3/notices/search",
                                    "HTTP 503 after 4 attempts")

    root = make_repo(tmp_path)
    summary = run(root, "2026-08-01", OutageClient([], {}))
    record = read_json(root / "snapshots" / "2026-08-01" / "run.json")
    assert summary["failures"] == 1
    assert record["failures"][0]["scope"].startswith("search:")
    assert record["new_matches"] == []
