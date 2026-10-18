#!/usr/bin/env python3
"""Re-derive the two load-bearing facts behind this case from committed,
manifested bytes only: (1) where the envelope phrase 'artificial intelligence'
actually occurs in notice 690422-2026, and (2) the procedure metadata that
shows this is one framework-agreement award, not five independent contracts.

Run: python cases/c-20261007-05/analysis/inspect_notice.py --repo-root ../../..
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

NOTICE = "snapshots/2026-10-07/notices/690422-2026.xml"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    text = (root / NOTICE).read_text(encoding="utf-8")
    lowered = text.lower()

    phrase = "artificial intelligence"
    hits = [m.start() for m in re.finditer(re.escape(phrase), lowered)]
    print(f"occurrences of {phrase!r} in {NOTICE}: {len(hits)}")
    for pos in hits:
        window = text[max(0, pos - 160):pos + 160].replace("\n", " ")
        print(f"  context: ...{window}...")

    fields = {
        "procedure type": r'<cbc:ProcedureCode[^>]*>([^<]*)</cbc:ProcedureCode>',
        "framework-agreement type": r'<cbc:ContractingSystemTypeCode listName="framework-agreement">([^<]*)</cbc:ContractingSystemTypeCode>',
        "notice subtype": r'<cbc:SubTypeCode[^>]*>([^<]*)</cbc:SubTypeCode>',
        "estimated value (EUR)": r'<cbc:EstimatedOverallContractAmount[^>]*>([^<]*)</cbc:EstimatedOverallContractAmount>',
        "duration (months)": r'<cbc:DurationMeasure unitCode="MONTH">([^<]*)</cbc:DurationMeasure>',
        "legal basis (regulatory domain)": r'<cbc:RegulatoryDomain>([^<]*)</cbc:RegulatoryDomain>',
    }
    print()
    print("procedure metadata (first match each):")
    for label, pattern in fields.items():
        m = re.search(pattern, text)
        print(f"  {label}: {m.group(1) if m else 'NOT FOUND'}")

    winner_names = sorted(set(re.findall(r'<cbc:Name[^>]*>([^<]*)</cbc:Name>', text)))
    print()
    print("distinct <cbc:Name> values in the document (buyers + winner, truncated):")
    for name in winner_names[:20]:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
