# Findings — c-20261007-05

**Terminal state: FALSE_ALARM**

## Proposition tested

"vendor 'ex libris' appears with buyers in 5 countries (BEL, DEU, LUX, MLT,
PRT) within 90 days — a cross-border vendor family is forming" (signal
`PATTERN:ex libris`, built from notice 690422-2026).

## What was tested

Three competing explanations (`analysis/explanations.md`):

- **A.** Clerical/structural artifact — the 5-country spread is the buyer
  list of one joint-procurement notice, not an accumulation across
  independent notices.
- **B.** Republication artifact — the notice is the award-stage publication
  of an already-public procedure, not new information.
- **C.** Genuine finding — a newly consolidating, EU-institution-wide,
  single-vendor dependency worth tracking.

Each was checked against the preserved notice XML and three TED Search API
responses fetched during this investigation (`cases/c-20261007-05/evidence/`,
scripts in `cases/c-20261007-05/analysis/`).

## What survived

- The sentinel's `vendor_patterns()` detector (`sentinel/src/sentinel/signals.py`)
  unions buyer countries across notices sharing a vendor key within a
  90-day window and fires at ≥2 countries. It does not distinguish "2
  countries from 2 independent notices" from "2 countries because 1 notice
  already lists buyers in 2 countries." Here, all 5 countries come from a
  single lot, single framework-agreement award, single winner ("EX
  LIBRIS"), shared by 12 named EU-institution buyers (AMLA, CONSIL, COR,
  CURIA, ECA, EEAS, EESC, EP, EUAA, EUCOM, EUDA, PUBL). There is no
  accumulation across separate decisions — explanation A holds.
- A contract notice for the identical 12-buyer set, identical CPV code
  (72212160) and identical multilingual title (57057-2026) was already
  public on 2026-01-26, more than 8 months before the award notice that
  triggered this candidate. The award is not new information about a
  forming relationship; it is the scheduled second half of an already
  visible procedure — explanation B holds.
- The candidate's own gate (`sentinel/src/sentinel/gate.py`) passes
  `consequential_relation` unconditionally for every PATTERN signal
  ("cross-border vendor recurrence is consequential by construction"),
  without checking whether the countries originate from one notice or many.
  That is a gap in the gate, not evidence of a real pattern here.
- The reason notice 690422-2026 is in the AI-procurement envelope at all:
  the phrase "artificial intelligence" occurs exactly once in the document,
  inside the postal address of the buyer's contact department
  ("OP.A — ... and Artificial Intelligence Exploitation"), not in any
  description of the procured Library Services Platform. This is
  acknowledged, expected bycatch of a phrase-only envelope
  (`envelope/queries.json`), not a sign of AI-specific procurement.
- A TED-wide check (winner-name "ex libris" + CPV 72212160) found only two
  other "ex libris" contract awards in the whole index, each naming a
  single buyer country (Italy 2024, Netherlands 2025) — no broader,
  independently accumulating cross-border footprint that the narrower
  checks above might have missed.

## What died

- Explanation C (a genuinely new, consolidating multi-institution
  dependency) does not survive: there is exactly one decision point (one
  lot, one award), already previewed 8 months earlier, not a sequence of
  independent events forming a pattern over time.
- The implicit premise of the signal's own detail text — that this is a
  *process* ("is forming") rather than a already-decided, already-announced
  *outcome* — does not survive contact with the contract notice / award
  notice pair.

## Why FALSE_ALARM, not INTERESTING_BUT_TRIVIAL

The underlying fact (12 EU institutions sharing one 8-year, €9,000,000,
no-reopening-of-competition framework agreement with a single vendor) is a
legitimate, large, and plausibly consequential administrative decision — not
nothing. But the signal as stated is not that story: it claims a *forming*
cross-border vendor family, built additively from recurrence, when the
record shows one already-closed procurement act whose multi-country,
multi-buyer shape was fixed from the first public notice in January 2026.
The thing the signal says is happening (an emerging pattern, visible only
through machine-scale comparison across separate notices) is not what is
actually happening (one procedure, legible from a single document). That
distinction is exactly what `verify.py`'s falsifiability bar exists to
catch: the proposition, read literally, is false.

A secondary, systemic observation worth carrying forward without opening a
new case: the PATTERN detector and the gate's `consequential_relation`
check for it should distinguish "countries accumulated across separate
notices" from "countries present within a single notice's buyer list" —
otherwise every future joint/interinstitutional procurement notice with
≥2 participating countries will trigger an identical false PATTERN signal.
This is a detector-design note, not an accusation and not something this
case resolves.
