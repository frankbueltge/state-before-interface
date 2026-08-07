"""The candidate gate: six criteria, each decided deterministically with a
written reason. A candidate is OPEN only if all six pass. Most candidates are
expected to die here — a committed DECLINED is a successful outcome (I7).
"""

from __future__ import annotations

from .preserve import utc_now
from . import signals as sig

CRITERIA = (
    "observable_public_problem",
    "machine_readable_evidence",
    "consequential_relation",
    "machine_scale_advantage",
    "falsifiable_investigation",
    "digital_form_possible",
)

# Conservative multilingual markers for administrative functions where an
# AI purchase touches people's lives directly (Annex-III-adjacent domains).
SENSITIVE_KEYWORDS = (
    "employment", "unemploy", "welfare", "social security", "social benefit",
    "beschäftigung", "arbeitsmarkt", "arbeitslos", "sozialleistung", "sozialhilfe",
    "emploi", "chômage", "aide sociale", "sécurité sociale",
    "police", "policing", "polizei", "justice", "justiz", "gericht",
    "court", "tribunal", "prison",
    "migration", "asylum", "asyl", "asile", "border control", "grenzschutz", "frontière",
    "health", "hospital", "gesundheit", "krankenhaus", "klinik", "santé", "hôpital",
    "education", "school", "bildung", "schule", "université", "école", "éducation",
    "taxation", "steuerverwaltung", "impôt",
)

SENSITIVE_CPV_PREFIXES = ("75", "80", "85")

FORM_HYPOTHESES = {
    sig.CHANGED_NOTICE: "superimposed text states of the same record",
    sig.DISAPPEARED: "a registry of holes: the preserved record and its public absence",
    sig.PATTERN: "a vendor constellation across buyers and countries",
    sig.NEW_MATCH: "an annotated dossier along the structure of the notice",
}


def _entries(signal: dict, notices_index: dict) -> list[tuple[str, dict]]:
    return [(p, notices_index[p]) for p in signal["notices"] if p in notices_index]


def _sensitive_hit(entry: dict) -> str | None:
    for title in entry.get("titles", []):
        low = title.casefold()
        for kw in SENSITIVE_KEYWORDS:
            if kw in low:
                return f"title marker '{kw}'"
    for cpv in entry.get("cpv", []):
        if str(cpv)[:2] in SENSITIVE_CPV_PREFIXES:
            return f"CPV {cpv} (prefix {str(cpv)[:2]})"
    return None


def _prior_context(pubnum: str, entry: dict, notices_index: dict) -> str | None:
    buyers = set(entry.get("buyer_names", []))
    vendors = {v for v in entry.get("vendor_keys", []) if v}
    for other_pub, other in sorted(notices_index.items()):
        if other_pub == pubnum or other["first_seen"] >= entry["first_seen"]:
            continue
        shared_buyer = buyers & set(other.get("buyer_names", []))
        if shared_buyer:
            return f"buyer '{sorted(shared_buyer)[0]}' already on record ({other_pub})"
        shared_vendor = vendors & set(other.get("vendor_keys", []))
        if shared_vendor:
            return f"vendor '{sorted(shared_vendor)[0]}' already on record ({other_pub})"
    return None


def evaluate(signal: dict, notices_index: dict) -> dict:
    """Return a candidate record (without id) for a signal."""
    entries = _entries(signal, notices_index)
    criteria: dict[str, dict] = {}

    buyers = sorted({b for _, e in entries for b in e.get("buyer_names", [])})
    criteria["observable_public_problem"] = {
        "passed": bool(buyers),
        "reason": (f"identifiable public buyer(s): {', '.join(buyers[:5])}"
                   if buyers else "no identifiable buyer in the record"),
    }

    preserved = [p for p, e in entries if e.get("versions")]
    criteria["machine_readable_evidence"] = {
        "passed": bool(entries) and len(preserved) == len(entries),
        "reason": (f"{len(preserved)} preserved eForms XML record(s) with SHA-256 on file"
                   if entries and len(preserved) == len(entries)
                   else "not every referenced notice has preserved bytes"),
    }

    if signal["type"] == sig.PATTERN:
        criteria["consequential_relation"] = {
            "passed": True,
            "reason": "cross-border vendor recurrence is consequential by construction",
        }
    else:
        hits = [(p, _sensitive_hit(e)) for p, e in entries]
        hit = next(((p, h) for p, h in hits if h), None)
        criteria["consequential_relation"] = {
            "passed": hit is not None,
            "reason": (f"touches a sensitive administrative domain: {hit[1]} ({hit[0]})"
                       if hit else
                       "no marker of a sensitive administrative domain "
                       "(employment, welfare, policing, migration, health, "
                       "education, justice, taxation)"),
        }

    if signal["type"] in (sig.CHANGED_NOTICE, sig.DISAPPEARED, sig.PATTERN):
        criteria["machine_scale_advantage"] = {
            "passed": True,
            "reason": f"{signal['type']} is only visible through continuous "
                      "preservation and comparison — not to a human reader of "
                      "a single day's journal",
        }
        context = None
    else:
        pubnum, entry = entries[0] if entries else (signal["notices"][0], {})
        context = _prior_context(pubnum, entry, notices_index) if entry else None
        criteria["machine_scale_advantage"] = {
            "passed": context is not None,
            "reason": (f"machine memory relates this record to prior records: {context}"
                       if context else
                       "a single first-seen notice is equally visible to any "
                       "human reader of the journal"),
        }

    proposition = _proposition(signal, entries, context)
    criteria["falsifiable_investigation"] = {
        "passed": proposition is not None,
        "reason": (f"testable proposition: {proposition}" if proposition
                   else "no machine-testable proposition can be formed yet"),
    }

    form = FORM_HYPOTHESES[signal["type"]]
    criteria["digital_form_possible"] = {
        "passed": True,
        "reason": f"form hypothesis: {form}",
    }

    verdict = "OPEN" if all(c["passed"] for c in criteria.values()) else "DECLINED"
    return {
        "created": utc_now(),
        "signal": signal,
        "criteria": criteria,
        "verdict": verdict,
        "proposition": proposition,
        "form_hypothesis": form,
        "notices_context": [
            {"publication_number": p,
             "title": e.get("title", ""),
             "buyers": e.get("buyer_names", []),
             "countries": e.get("buyer_countries", [])}
            for p, e in entries
        ],
    }


def _proposition(signal: dict, entries, context: str | None) -> str | None:
    kind = signal["type"]
    if kind == sig.CHANGED_NOTICE:
        return (f"the preserved record of notice {signal['notices'][0]} changed "
                "after publication in a way that alters substance "
                "(scope, value or AI wording), not merely presentation")
    if kind == sig.DISAPPEARED:
        return (f"notice {signal['notices'][0]}, previously retrievable and "
                "hashed, is no longer publicly retrievable")
    if kind == sig.PATTERN:
        return (f"{signal['detail']} — a cross-border vendor family is forming")
    if kind == sig.NEW_MATCH and context:
        return (f"{context} — this is a sustained procurement programme, "
                "not a one-off purchase")
    return None
