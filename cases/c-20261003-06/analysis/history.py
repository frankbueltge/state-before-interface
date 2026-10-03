#!/usr/bin/env python3
"""Re-runnable analysis for case c-20261003-06.

Tests E1 (is 676246-2026 the award stage of an already-public call for
tenders?) and E2/E3 (is DG CNECT's AI-related TED footprint a dense,
continuous, multi-year stream, or an isolated cluster?) against the
evidence preserved under cases/c-20261003-06/evidence/.

Stdlib only. Run from the repo root:
    python3 cases/c-20261003-06/analysis/history.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "cases" / "c-20261003-06" / "evidence"
SNAPSHOT_NOTICES = ROOT / "snapshots" / "2026-10-03" / "notices"


def check_e1() -> dict:
    """676246-2026 (and sibling 677429-2026) vs the original call for tenders."""
    cn_text = (EVIDENCE / "115144-2026.xml").read_text(encoding="utf-8")
    cn_project_ids = set(re.findall(r"<cbc:ID>(EC-CNECT/[^<]*)</cbc:ID>", cn_text))

    results = {}
    for pubnum in ("676246-2026", "677429-2026"):
        can_text = (SNAPSHOT_NOTICES / f"{pubnum}.xml").read_text(encoding="utf-8")
        referenced_cn = re.findall(
            r"<cac:NoticeDocumentReference>\s*<cbc:ID>([^<]*)</cbc:ID>", can_text)
        award_project_ids = set(re.findall(r"<cbc:ID>(EC-CNECT/[^<]*)</cbc:ID>", can_text))
        results[pubnum] = {
            "references_notice": referenced_cn,
            "references_115144-2026": "115144-2026" in referenced_cn,
            "shares_project_id_with_cn": bool(award_project_ids & cn_project_ids),
            "project_ids": sorted(award_project_ids),
        }
    return {
        "cn_notice": "115144-2026",
        "cn_issue_date": re.findall(r"<cbc:IssueDate>([^<]*)</cbc:IssueDate>", cn_text)[0],
        "cn_project_ids": sorted(cn_project_ids),
        "awards": results,
    }


def check_e2_e3() -> dict:
    """Full public history of DG CNECT notices mentioning 'artificial intelligence'."""
    data = json.loads((EVIDENCE / "ted-search-dgcnect-ai-history.json").read_text())
    notices = data["notices"]
    by_year = {}
    by_type = {}
    for n in notices:
        year = n["publication-number"].split("-")[-1]
        by_year[year] = by_year.get(year, 0) + 1
        ntype = n.get("notice-type", "?")
        by_type[ntype] = by_type.get(ntype, 0) + 1

    timeline = sorted(
        (n["publication-date"], n["publication-number"], n.get("notice-type"),
         n.get("notice-title", {}).get("eng", "<no English title>"))
        for n in notices
    )
    return {
        "query": "FT=(\"DG CNECT\") AND FT=(\"artificial intelligence\")",
        "total_notice_count": data["totalNoticeCount"],
        "returned": len(notices),
        "by_year": dict(sorted(by_year.items())),
        "by_notice_type": dict(sorted(by_type.items())),
        "first_publication_date": timeline[0][0],
        "last_publication_date": timeline[-1][0],
        "timeline": [
            {"date": d, "publication_number": p, "notice_type": t, "title_eng": title}
            for d, p, t, title in timeline
        ],
    }


def check_recurring_editions() -> dict:
    """Does 'AI for Public Good' recur under a distinct, earlier project ID,
    and what happened to Lot 1 (Health) the first time it was run?"""
    cn_2024 = (EVIDENCE / "484917-2025.xml").read_text(encoding="utf-8")
    can_2024_lot1 = (EVIDENCE / "762241-2025.xml").read_text(encoding="utf-8")
    lot1_2026 = (SNAPSHOT_NOTICES / "677429-2026.xml").read_text(encoding="utf-8")

    project_ids_2024 = set(re.findall(r"<cbc:ID>(EC-CNECT/[^<]*)</cbc:ID>", cn_2024))
    referenced = re.findall(
        r"<cac:NoticeDocumentReference>\s*<cbc:ID>([^<]*)</cbc:ID>", can_2024_lot1)
    lot1_2024_status = re.findall(
        r'listName="winner-selection-status">([^<]*)', can_2024_lot1)
    lot1_2024_reason = re.findall(
        r'listName="non-award-justification">([^<]*)', can_2024_lot1)
    lot1_2024_submissions = re.findall(
        r'<efbc:StatisticsCode listName="received-submission-type">t-esubm</efbc:StatisticsCode>'
        r'\s*<efbc:StatisticsNumeric>(\d+)</efbc:StatisticsNumeric>', can_2024_lot1)

    lot1_2026_status = re.findall(
        r'listName="winner-selection-status">([^<]*)', lot1_2026)
    lot1_2026_amount = re.findall(
        r'<cbc:TotalAmount currencyID="EUR">([^<]*)</cbc:TotalAmount>', lot1_2026)
    lot1_2026_winners = re.findall(r'<cbc:Name languageID="ENG">([^<]*)</cbc:Name>', lot1_2026)

    return {
        "edition_2024_2025": {
            "cn_notice": "484917-2025",
            "cn_issue_date": re.findall(r"<cbc:IssueDate>([^<]*)</cbc:IssueDate>", cn_2024)[0],
            "project_ids": sorted(project_ids_2024),
            "lot1_award_notice": "762241-2025",
            "lot1_award_references_cn": "484917-2025" in referenced,
            "lot1_winner_selection_status": lot1_2024_status,
            "lot1_non_award_justification": lot1_2024_reason,
            "lot1_electronic_submissions_received": lot1_2024_submissions,
        },
        "edition_2026": {
            "cn_notice": "115144-2026",
            "project_ids": ["EC-CNECT/2026/OP/0003", "EC-CNECT/2026/OP/0003-LOT-1",
                             "EC-CNECT/2026/OP/0003-LOT-2"],
            "lot1_award_notice": "677429-2026",
            "lot1_winner_selection_status": lot1_2026_status,
            "lot1_awarded_amount_eur": lot1_2026_amount,
            "lot1_organizations_mentioned": lot1_2026_winners[:5],
        },
        "same_title_different_project_id": (
            "EC-CNECT/2024/OP/0094" in project_ids_2024
            and "EC-CNECT/2026/OP/0003" not in project_ids_2024
        ),
        "conclusion": "Lot 1 (Health: cancer imaging) of the first "
                       "'AI for Public Good' edition (EC-CNECT/2024/OP/0094) "
                       "received 11 electronic submissions but closed without "
                       "a winner ('clos-nw', non-award-justification 'other'). "
                       "The second edition (EC-CNECT/2026/OP/0003), with an "
                       "identical estimated budget, re-ran the same lot and "
                       "awarded it. Lot 2 (Energy) was awarded in the second "
                       "edition; the first edition's Lot 2 result "
                       "(763846-2025) could not be retrieved (HTTP 202 on "
                       "every attempt, see adversarial.md) and is not claimed.",
    }


def main() -> None:
    out = {
        "e1_award_follows_prior_public_cn": check_e1(),
        "e2_e3_dgcnect_ai_history": check_e2_e3(),
        "recurring_ai_for_public_good_editions": check_recurring_editions(),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
