#!/usr/bin/env python3
"""Cross-reference the signal notice (677429-2026) against the buyer's other
preserved AI-tagged notices to test the proposition: 'European Commission,
DG CNECT' is a sustained AI procurement buyer, not a one-off.

Re-run from the repo root:
    python cases/c-20261003-09/analysis/crossref.py --repo-root .

Pure stdlib (re module), reads only committed/preserved bytes, writes
crossref_output.json next to this script.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NOTICES = {
    "560875-2026": "snapshots/2026-08-16/notices/560875-2026.xml",
    "676246-2026": "snapshots/2026-10-03/notices/676246-2026.xml",
    "677429-2026": "snapshots/2026-10-03/notices/677429-2026.xml",
    "115144-2026": "cases/c-20261003-09/evidence/115144-2026.xml",
}


def grab(pattern: str, text: str):
    return re.findall(pattern, text)


def analyse(root: Path) -> dict:
    texts = {k: (root / v).read_text(encoding="utf-8") for k, v in NOTICES.items()}

    out = {}
    for key, text in texts.items():
        folder = grab(r"<cbc:ContractFolderID>([^<]*)</cbc:ContractFolderID>", text)
        procedure = sorted(set(grab(r"<cbc:ID>(EC-CNECT/\d{4}/OP/\d+)</cbc:ID>", text)))
        amounts = grab(r'<cbc:PayableAmount currencyID="EUR">([^<]*)</cbc:PayableAmount>', text)
        estimates = grab(
            r'<cbc:EstimatedOverallContractAmount currencyID="EUR">([^<]*)'
            r"</cbc:EstimatedOverallContractAmount>", text)
        issue_dates = grab(r"<cbc:IssueDate>([^<]*)</cbc:IssueDate>", text)
        lot_refs = sorted(set(grab(r'<cbc:ID schemeName="Lot">([^<]*)</cbc:ID>', text)))
        out[key] = {
            "contract_folder_id": folder[0] if folder else None,
            "procedure_id": procedure,
            "payable_amounts_eur": amounts,
            "estimated_amounts_eur": estimates,
            "issue_dates": issue_dates,
            "lot_ids": lot_refs,
        }

    same_folder = out["676246-2026"]["contract_folder_id"] == out["677429-2026"]["contract_folder_id"] \
        == out["115144-2026"]["contract_folder_id"]
    same_procedure = (out["676246-2026"]["procedure_id"] == out["677429-2026"]["procedure_id"]
                       == out["115144-2026"]["procedure_id"] != [])
    different_procedure_from_chatbots = (
        out["560875-2026"]["procedure_id"] != out["677429-2026"]["procedure_id"]
    )

    verdict = {
        "lots_676246_and_677429_are_one_tender": bool(same_folder and same_procedure),
        "chatbot_notice_is_a_distinct_procedure": bool(different_procedure_from_chatbots),
        "distinct_dg_cnect_ai_procurement_tracks_in_envelope": 2 if (
            same_folder and same_procedure and different_procedure_from_chatbots) else None,
    }
    return {"per_notice": out, "verdict": verdict}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = analyse(root)
    out_path = Path(__file__).resolve().parent / "crossref_output.json"
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
