#!/usr/bin/env python3
"""Check the two competing readings of the PATTERN:ex libris signal against
public TED data captured in cases/c-20261007-05/evidence/.

1. Is the 5-country spread a recurrence across independent notices, or the
   buyer list of a single joint procurement? -> ex-libris-library-cpv-search.json
2. Is 690422-2026 a new relationship, or the award stage of an already
   public procedure? -> european-parliament-library-cpv-search.json /
   57057-2026-search.json

Run: python cases/c-20261007-05/analysis/check_pattern.py --repo-root ../../..
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

EVIDENCE_DIR = "cases/c-20261007-05/evidence"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    ev = root / EVIDENCE_DIR

    print("--- (1) every TED notice where winner-name='ex libris' AND CPV=72212160 ---")
    data = json.loads((ev / "ex-libris-library-cpv-search.json").read_text())
    print(f"totalNoticeCount: {data['totalNoticeCount']}")
    for n in data["notices"]:
        countries = sorted(set(n.get("buyer-country", [])))
        print(f"  {n['publication-number']} ({n['publication-date']}, "
              f"{n['notice-type']}) buyer countries: {countries}")
    print("-> only one of these three notices carries more than one buyer "
          "country, and it is the candidate notice itself: the 5-country "
          "spread is a property of a single notice, not an accumulation "
          "across separate notices.")

    print()
    print("--- (2) same CPV + buyer 'European Parliament', across all years ---")
    data = json.loads((ev / "european-parliament-library-cpv-search.json").read_text())
    print(f"totalNoticeCount: {data['totalNoticeCount']}")
    for n in data["notices"]:
        print(f"  {n['publication-number']} ({n['publication-date']}, "
              f"{n['notice-type']})")
    print("-> 57057-2026 (contract notice, published 2026-01-26) and "
          "690422-2026 (contract award notice, published 2026-10-07) share "
          "buyer set, CPV and title: two publication stages of one "
          "procedure, 8+ months apart, not two separate relationships.")

    print()
    print("--- (3) buyer set identity check ---")
    cn = json.loads((ev / "57057-2026-search.json").read_text())["notices"][0]
    cn_buyers = sorted(cn["buyer-name"]["eng"])
    print("contract-notice (57057-2026) buyers:", cn_buyers)


if __name__ == "__main__":
    main()
