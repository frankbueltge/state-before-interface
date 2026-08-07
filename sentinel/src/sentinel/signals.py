"""Difference detection: the sentinel does not look for "interesting news" but
for differences with research value, computed deterministically over the index.
"""

from __future__ import annotations

from datetime import date, timedelta

NEW_MATCH = "NEW_MATCH"
CHANGED_NOTICE = "CHANGED_NOTICE"
DISAPPEARED = "DISAPPEARED"
PATTERN = "PATTERN"


def new_match_signal(pubnum: str, phrases: list[str], day: str) -> dict:
    return {
        "type": NEW_MATCH,
        "key": f"{NEW_MATCH}:{pubnum}",
        "date": day,
        "notices": [pubnum],
        "detail": f"notice {pubnum} entered the envelope "
                  f"(phrases: {', '.join(sorted(phrases))})",
    }


def changed_signal(pubnum: str, old_sha: str, new_sha: str, day: str) -> dict:
    return {
        "type": CHANGED_NOTICE,
        "key": f"{CHANGED_NOTICE}:{pubnum}:{new_sha[:12]}",
        "date": day,
        "notices": [pubnum],
        "detail": f"preserved bytes of notice {pubnum} changed "
                  f"({old_sha[:12]}… → {new_sha[:12]}…)",
    }


def disappeared_signal(pubnum: str, http_status: int, day: str) -> dict:
    return {
        "type": DISAPPEARED,
        "key": f"{DISAPPEARED}:{pubnum}",
        "date": day,
        "notices": [pubnum],
        "detail": f"notice {pubnum}, previously retrievable, now returns "
                  f"HTTP {http_status}",
    }


def vendor_patterns(notices_index: dict, day: str, window_days: int) -> list[dict]:
    """Same normalized vendor with buyers in >= 2 countries within the window."""
    cutoff = (date.fromisoformat(day) - timedelta(days=window_days)).isoformat()
    vendors: dict[str, dict] = {}
    for pubnum, entry in sorted(notices_index.items()):
        if entry["first_seen"] < cutoff:
            continue
        for key in entry.get("vendor_keys", []):
            if not key:
                continue
            record = vendors.setdefault(key, {"countries": set(), "notices": []})
            record["countries"].update(entry.get("buyer_countries", []))
            record["notices"].append(pubnum)
    signals = []
    for key, record in sorted(vendors.items()):
        if len(record["countries"]) >= 2:
            signals.append({
                "type": PATTERN,
                "key": f"{PATTERN}:{key}",
                "date": day,
                "notices": sorted(record["notices"]),
                "detail": f"vendor '{key}' appears with buyers in "
                          f"{len(record['countries'])} countries "
                          f"({', '.join(sorted(record['countries']))}) "
                          f"within {window_days} days",
            })
    return signals
