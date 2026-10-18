# Findings — c-20261003-06

**Terminal state: RESEARCH_RESULT**

## What was tested

The gate's proposition was narrow: buyer "European Commission, DG CNECT"
is already on record (560875-2026), so notice 676246-2026 is evidence of a
*sustained procurement programme*, not a one-off purchase. Three competing
explanations were set up in `analysis/explanations.md`:

- **E1** — boring: the award notice is just the routine award stage of an
  already-public call for tenders, not a new procurement event at all.
- **E2** — boring: DG CNECT's AI Office has a mandate that predicts
  multiple AI procurements per year; "a programme" would be unremarkable.
- **E3** — the proposition taken seriously: the pattern is more specific
  and more interesting than "DG CNECT buys a lot of IT."

## What survived, what died

**E1 survived and is confirmed as fact, not as a reason to close the
case.** `676246-2026` and its sibling `677429-2026` are indeed the award
stage of contract notice `115144-2026` (published 2026-02-17, same
`ContractFolderID`). This is not news — see `claims.json` claim 1 — but it
only establishes that the sentinel's "NEW_MATCH" label means "newly
entered the envelope," not "newly announced."

**E2 survived and is confirmed, also not sufficient on its own.** DG CNECT
published at least 27 AI-tagged TED notices across 26 months (2024-08-06 to
2026-10-01), spanning five distinct thematic lines (claim 2). An AI Office
running many AI procurements is exactly what its stated mandate predicts.
On its own this would close the case as `INTERESTING_BUT_TRIVIAL`.

**E3 is what keeps the case open as a result, and it is narrower and more
specific than the original proposition.** The cross-notice correlation that
only a machine with persistent memory of past notices can make cheaply
(the observatory's own "machine-scale advantage" criterion) surfaces a
concrete, falsifiable, non-accusatory fact that is not visible from any
single notice:

> "AI for Public Good" (Lot 1 Health: AI-based cancer imaging for breast
> and prostate diagnosis; Lot 2 Energy: AI-based grid optimisation) is not
> a one-off call. It was run twice, under distinct contract folders,
> fifteen months apart, with an **identical** estimated budget split
> (EUR 5.4M / 2.4M / 3.0M) in both editions. In the first edition
> (`EC-CNECT/2024/OP/0094`), Lot 1 received 11 electronic submissions and
> closed **without a contract being awarded** ("clos-nw" / non-award
> justification "other"). The lot was then re-run, unchanged in scope and
> budget, as part of the second edition (`EC-CNECT/2026/OP/0003`), and this
> time was awarded (2026-09-04, EUR 2,060,727.30, to a consortium including
> Fundação Champalimaud).

This is a factual, org-level, falsifiable statement with a complete,
verifiable evidence chain (`claims.json` claims 3–5). It describes a
public-procurement pattern, not a wrongdoing — no individual or
organization is accused of anything; the record simply shows a
public-health-relevant AI research lot that failed once and succeeded on
retry, fully visible on TED, fully explained by ordinary tender outcomes
(an "other" non-award justification covers many legitimate reasons: no
compliant bid, budget mismatch, withdrawal, etc., none of which this
investigation can or should adjudicate).

## What died

The sibling Lot 2 (Energy) result from the first edition (`763846-2025`)
could not be retrieved — the TED XML endpoint returned `HTTP 202` with an
empty body on every attempt across roughly 45 seconds of retries on
2026-10-03 (`analysis/adversarial.md`, attempt 4). Per invariant I4 this is
recorded as a source outage, not resolved by inference from the search
API's summary field (which showed a `total-value` equal to the full
project estimate, too ambiguous to use as evidence of either an award or a
non-award). No claim is made about the first edition's Lot 2 outcome.

A full negative-control comparison against other EU Directorates-General's
TED density (to confirm the 27-notice count is unusual, not typical of any
large EU buyer) was not run — it would require a new, open-ended TED query
strategy disproportionate to this case's scope, and is flagged as an
unclosed thread in `analysis/adversarial.md` rather than silently assumed.

## Form

Digital form: a derived timeline/dossier comparing the two "AI for Public
Good" editions side by side, lot by lot, drawn directly from the
structure the eForms notices already use (`ProcurementProject` →
`ProcurementProjectLot` → `TenderResult`/`LotResult`): two columns (2024/2025
edition, 2026 edition), each broken into the same three stages (contract
notice → lot 1 result → lot 2 result), annotated only with facts carried in
`claims.json`. See `form/index.html`; derivation rationale repeated there
in an HTML comment at the top of the file.
