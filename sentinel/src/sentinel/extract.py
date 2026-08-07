"""Field extraction under invariant I8: derived data may only carry
organization-level fields from an explicit whitelist. Contact persons and any
non-whitelisted structure never leave the preserved raw record.
"""

from __future__ import annotations

import re

# The only search-response fields that may flow into derived data.
FIELD_WHITELIST = (
    "publication-number",
    "publication-date",
    "notice-title",
    "buyer-name",
    "buyer-country",
    "winner-name",
    "total-value",
    "total-value-cur",
    "classification-cpv",
    "notice-type",
)

_LEGAL_SUFFIXES = (
    "gmbh & co. kg", "gmbh", "ag", "se", "kg", "e.v.", "ev",
    "a/s", "as", "aps", "ab", "oy", "asa",
    "s.p.a.", "spa", "s.r.l.", "srl", "s.a.", "sa", "s.a.s.", "sas",
    "s.à r.l.", "sarl", "sp. z o.o.", "d.o.o.", "doo",
    "b.v.", "bv", "n.v.", "nv", "ltd", "limited", "llc", "inc", "plc",
)


def slim(notice: dict) -> dict:
    """Reduce a raw search hit to whitelisted fields (drops links, contacts, …)."""
    return {k: notice[k] for k in FIELD_WHITELIST if k in notice}


def names(field: dict | list | None) -> list[str]:
    """Flatten a multilingual name field ({lang: [names]}) to a sorted list."""
    if field is None:
        return []
    values: list[str] = []
    if isinstance(field, dict):
        for entry in field.values():
            values.extend(entry if isinstance(entry, list) else [entry])
    elif isinstance(field, list):
        values = [str(v) for v in field]
    return sorted({v.strip() for v in values if isinstance(v, str) and v.strip()})


def titles(field: dict | str | None) -> list[str]:
    """All language versions of a notice title."""
    if field is None:
        return []
    if isinstance(field, str):
        return [field]
    return sorted({v for v in field.values() if isinstance(v, str)})


def title_display(field: dict | str | None) -> str:
    """One human-readable title, preferring English."""
    if isinstance(field, str):
        return field
    if isinstance(field, dict):
        return field.get("eng") or next(iter(sorted(field.items())), (None, ""))[1]
    return ""


def normalize_vendor(name: str) -> str:
    """Conservative vendor key: casefold, strip punctuation and legal suffixes."""
    key = re.sub(r"[^\w\s]", " ", name.casefold())
    key = re.sub(r"\s+", " ", key).strip()
    for suffix in _LEGAL_SUFFIXES:
        bare = re.sub(r"[^\w\s]", " ", suffix)
        bare = re.sub(r"\s+", " ", bare).strip()
        if key.endswith(" " + bare):
            key = key[: -len(bare) - 1].strip()
            break
    return key
