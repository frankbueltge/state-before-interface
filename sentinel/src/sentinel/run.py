"""The nightly sentinel run: observe → preserve → diff → gate → records.

Deterministic by design: no model is involved. Every outcome — including
"no signal" — is committed as a dated record. Invariants I1, I3, I4, I6, I8.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from . import autonomy, gate
from . import signals as sig
from .extract import (FIELD_WHITELIST, names, normalize_vendor, slim,
                      title_display, titles)
from .fetch import SEARCH_URL, SourceUnavailable, TedClient
from .preserve import Snapshot, read_json, sha256, utc_now, write_json

CASE_INITIAL_STATE = "CASE_OPEN"


def _slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.casefold()).strip("-")


def _xml_url(raw_notice: dict, pubnum: str) -> str:
    links = raw_notice.get("links") or {}
    return (links.get("xml") or {}).get("MUL") or \
        f"https://ted.europa.eu/en/notice/{pubnum}/xml"


def run(repo_root: Path, day: str, client: TedClient | None = None) -> dict:
    client = client or TedClient()
    envelope = read_json(repo_root / "envelope" / "queries.json")
    index_path = repo_root / "snapshots" / "index.json"
    index = read_json(index_path, {"notices": {}, "emitted": []})
    notices_idx: dict = index["notices"]

    snap = Snapshot(repo_root, day)
    run_path = snap.dir / "run.json"
    if run_path.exists():
        raise SystemExit(f"run for {day} already recorded; snapshots are append-only (I3)")

    lookback = (date.fromisoformat(day)
                - timedelta(days=envelope["lookback_days"])).strftime("%Y%m%d")
    failures: list[dict] = []
    phrase_stats: list[dict] = []
    hits: dict[str, dict] = {}

    for phrase in envelope["phrases"]:
        query = f'FT=("{phrase["text"]}") AND publication-date>={lookback}'
        try:
            notices, total, truncated, raw_pages = client.search_all(
                query, list(FIELD_WHITELIST))
        except SourceUnavailable as err:
            failures.append({"scope": f"search:{phrase['text']}", "error": str(err)})
            continue
        for page_no, raw in enumerate(raw_pages, start=1):
            snap.preserve(f"search/{_slug(phrase['text'])}-p{page_no}.json",
                          raw, SEARCH_URL, 200)
        phrase_stats.append({"phrase": phrase["text"], "lang": phrase["lang"],
                             "total": total, "truncated": truncated})
        for notice in notices:
            pubnum = notice.get("publication-number")
            if not pubnum:
                failures.append({"scope": "search", "error": "hit without publication-number"})
                continue
            hit = hits.setdefault(pubnum, {"raw": notice, "phrases": set()})
            hit["phrases"].add(phrase["text"])

    day_signals: list[dict] = []

    new_pubs = sorted(p for p in hits if p not in notices_idx)
    for pubnum in new_pubs:
        raw = hits[pubnum]["raw"]
        xml_url = _xml_url(raw, pubnum)
        try:
            data, status = client.fetch_document(xml_url)
        except SourceUnavailable as err:
            failures.append({"scope": f"xml:{pubnum}", "error": str(err)})
            continue
        if status != 200:
            failures.append({"scope": f"xml:{pubnum}", "error": f"HTTP {status}"})
            continue
        manifest_entry = snap.preserve(f"notices/{pubnum}.xml", data, xml_url, status)
        record = slim(raw)
        winner_names = names(record.get("winner-name"))
        notices_idx[pubnum] = {
            "first_seen": day,
            "phrases": sorted(hits[pubnum]["phrases"]),
            "publication_date": str(record.get("publication-date", ""))[:10],
            "title": title_display(record.get("notice-title")),
            "titles": titles(record.get("notice-title")),
            "buyer_names": names(record.get("buyer-name")),
            "buyer_countries": names(record.get("buyer-country")),
            "winner_names": winner_names,
            "vendor_keys": sorted({normalize_vendor(w) for w in winner_names} - {""}),
            "cpv": sorted({str(c) for c in (record.get("classification-cpv") or [])}),
            "notice_type": record.get("notice-type"),
            "xml_url": xml_url,
            "gone": False,
            "last_checked": day,
            "versions": [{"date": day, "file": manifest_entry["file"],
                          "sha256": manifest_entry["sha256"]}],
        }
        day_signals.append(sig.new_match_signal(
            pubnum, notices_idx[pubnum]["phrases"], day))

    change_cutoff = (date.fromisoformat(day)
                     - timedelta(days=envelope["change_window_days"])).isoformat()
    new_set = set(new_pubs)
    recheck = [p for p, e in sorted(notices_idx.items())
               if p not in new_set and not e["gone"]
               and e["first_seen"] >= change_cutoff]
    for pubnum in recheck:
        entry = notices_idx[pubnum]
        try:
            data, status = client.fetch_document(entry["xml_url"])
        except SourceUnavailable as err:
            failures.append({"scope": f"recheck:{pubnum}", "error": str(err)})
            continue
        entry["last_checked"] = day
        if status in (404, 410):
            entry["gone"] = True
            day_signals.append(sig.disappeared_signal(pubnum, status, day))
            continue
        if status != 200:
            failures.append({"scope": f"recheck:{pubnum}", "error": f"HTTP {status}"})
            continue
        new_sha = sha256(data)
        old_sha = entry["versions"][-1]["sha256"]
        if new_sha != old_sha:
            manifest_entry = snap.preserve(f"notices/{pubnum}.xml", data,
                                           entry["xml_url"], status)
            entry["versions"].append({"date": day, "file": manifest_entry["file"],
                                      "sha256": manifest_entry["sha256"]})
            day_signals.append(sig.changed_signal(pubnum, old_sha, new_sha, day))

    day_signals.extend(sig.vendor_patterns(
        notices_idx, day, envelope["pattern_window_days"]))

    emitted = set(index["emitted"])
    opened: list[str] = []
    declined: list[str] = []
    run_signals: list[dict] = []
    seq = 0
    for signal in day_signals:
        if signal["key"] in emitted:
            continue
        emitted.add(signal["key"])
        index["emitted"].append(signal["key"])
        seq += 1
        cid = f"c-{day.replace('-', '')}-{seq:02d}"
        candidate = {"id": cid, **gate.evaluate(signal, notices_idx)}
        write_json(repo_root / "candidates" / f"{cid}.json", candidate)
        run_signals.append({"candidate": cid,
                            **{k: signal[k] for k in ("type", "key", "detail", "notices")}})
        if candidate["verdict"] == "OPEN":
            opened.append(cid)
            case_dir = repo_root / "cases" / cid
            write_json(case_dir / "state.json",
                       {"case": cid, "state": CASE_INITIAL_STATE,
                        "history": [{"ts": utc_now(), "state": CASE_INITIAL_STATE,
                                     "by": "sentinel-gate"}]})
            autonomy.append_line(case_dir / "log.jsonl", "case-open", "machine",
                                 detail={"candidate": cid, "signal": signal["key"]})
        else:
            declined.append(cid)

    snap.write_manifest()
    write_json(run_path, {
        "date": day,
        "envelope_version": envelope["version"],
        "phrases": phrase_stats,
        "failures": failures,
        "requests": client.requests,
        "http_429": client.http_429,
        "new_matches": new_pubs,
        "rechecked": len(recheck),
        "signals": run_signals,
        "candidates": {"open": opened, "declined": declined},
    })
    write_json(index_path, index)
    autonomy.append(repo_root, "sentinel-run", "machine", detail={
        "date": day, "requests": client.requests, "http_429": client.http_429,
        "new": len(new_pubs), "rechecked": len(recheck),
        "signals": len(run_signals), "open": len(opened),
        "declined": len(declined), "failures": len(failures)})
    return {"date": day, "opened": opened, "declined": declined,
            "new_matches": len(new_pubs), "signals": len(run_signals),
            "failures": len(failures)}


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Run the nightly sentinel.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--date",
                        default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--summary-out", type=Path, default=None)
    args = parser.parse_args(argv)

    summary = run(args.repo_root.resolve(), args.date)
    if args.summary_out:
        args.summary_out.write_text(json.dumps(summary) + "\n", encoding="utf-8")
    print(f"sentinel {summary['date']}: {summary['new_matches']} new, "
          f"{summary['signals']} signal(s), {len(summary['opened'])} opened, "
          f"{len(summary['declined'])} declined, {summary['failures']} failure(s)")


if __name__ == "__main__":
    main()
