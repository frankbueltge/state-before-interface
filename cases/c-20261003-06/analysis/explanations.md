# Competing explanations — c-20261003-06

Signal: `NEW_MATCH:676246-2026` — a contract award notice (eForms CAN,
subtype 29, `can-standard`) entered the sentinel's envelope on 2026-10-03.
Gate proposition under test: *"buyer European Commission, DG CNECT …
already on record (560875-2026) — this is a sustained procurement
programme, not a one-off purchase."*

## E1 — Clerical/republication artifact (boring, first)

The notice is not a new procurement action at all, just the routine award
stage of a competition whose call for tenders was already public months
earlier. If true, `676246-2026` should reference an earlier `cn-standard`
notice for the same project ID, and that earlier notice should already be
publicly dated well before the sentinel's 3-day lookback window.

**Confirms if:** the award notice's `TenderingProcess/NoticeDocumentReference`
points to a prior contract notice with the same `ProcurementProject/ID`.
**Kills if:** no such prior notice exists, or the project ID is unrelated —
i.e. the award really is the first public trace of this procurement.

## E2 — Genuine but unremarkable institutional routine (boring, second)

DG CNECT's Directorate A is explicitly named "Artificial Intelligence
Office" / "CNECT.A.5 — Artificial Intelligence for Societal Good" in the
notice's own buyer address block. A directorate with that mandate running
*multiple* AI-related procurements per year is exactly what its mandate
predicts, not a hidden pattern a machine needed to surface. If true, DG
CNECT's AI-related TED footprint should be a dense, continuous, multi-year
stream of ordinary notice types (PIN, CN, CAN) — not a cluster that
suddenly appeared.

**Confirms if:** a TED search for DG CNECT + "artificial intelligence"
(unrestricted by the sentinel's lookback/pattern windows) returns many
notices spread over a long period, of ordinary mixed types.
**Kills if:** the two prior notices (560875-2026, and the new one) are
in fact isolated/exceptional against a mostly AI-free buyer history.

## E3 — A programme worth naming (the proposition, taken seriously)

The "sustained programme" claim is literally true and non-trivial: DG
CNECT is running something that functions as a continuing programmatic
commitment of EU R&D money to AI pilots with public-sector/health/energy
targets, and the two notices the sentinel's own memory already linked
(560875-2026, 676246-2026) are only a fragment of a larger, otherwise
undifferentiated stream that is hard for a human reader of TED to see
because each notice is a separate record with no explicit "programme" tag.

**Confirms if:** the broader history shows a *coherent* thematic
programme (not just "DG CNECT buys lots of IT"), e.g. a named call
umbrella, repeated CPV/topic clustering, a funding-programme code tying
notices together (e.g. `HORIZONEU`), and a cadence that suggests ongoing
commitment rather than coincidence.
**Kills if:** the notices turn out to be a grab-bag of unrelated IT/legal/
research procurements that only share the buyer and the phrase "artificial
intelligence" picked up by full-text search (bycatch, as the envelope's
own rationale anticipates).

**Update after evidence acquisition:** E3 is confirmed more specifically
than expected. "AI for Public Good" (Lot 1 Health / Lot 2 Energy) is not
just thematically recurring — it is the *same* named call run twice under
distinct contract folders (`EC-CNECT/2024/OP/0094`, then
`EC-CNECT/2026/OP/0003`) with an identical €5.4M/€2.4M/€3M budget split.
Lot 1 of the first run closed with 11 submissions and no winner selected;
the re-run awarded it. See `adversarial.md` and `history_output.json`.

## What evidence resolves these

1. `cases/c-20261003-06/evidence/115144-2026.xml` — the original
   `cn-standard` contract notice for project `EC-CNECT/2026/OP/0003`,
   fetched to test E1.
2. `cases/c-20261003-06/evidence/ted-search-dgcnect-ai-history.json` — an
   unrestricted TED Search API v3 query (`FT=("DG CNECT") AND
   FT=("artificial intelligence")`) to test E2/E3 against the full public
   record, not just the sentinel's 90-day pattern window.
3. The two preserved award notices themselves
   (`snapshots/2026-10-03/notices/676246-2026.xml`,
   `snapshots/2026-10-03/notices/677429-2026.xml`, the latter being the
   sibling Lot 1 award under the separate open candidate c-20261003-09)
   and the prior record `560875-2026` already in `snapshots/index.json`.

See `cases/c-20261003-06/analysis/history.py` and its output
`cases/c-20261003-06/analysis/history_output.txt` for the computation, and
`cases/c-20261003-06/analysis/adversarial.md` for the attempt to kill E3.
