# Competing explanations — c-20261007-05

Signal: `PATTERN:ex libris` — "vendor 'ex libris' appears with buyers in 5
countries (BEL, DEU, LUX, MLT, PRT) within 90 days — a cross-border vendor
family is forming." Built from a single notice, 690422-2026.

## A. Clerical/structural artifact: one joint-procurement notice, not five
   relationships (boring explanation, tested first)

The sentinel's `vendor_patterns()` detector (`sentinel/src/sentinel/signals.py`)
unions `buyer_countries` across every notice carrying the same `vendor_keys`
entry within the 90-day window, and fires once the union reaches ≥2
countries. It does not distinguish "2 countries because 2 independent
notices each named one buyer" from "2 countries because 1 notice named
buyers from 2 countries." If the five-country spread comes from a single
notice describing one already-decided framework-agreement award, there is no
forming constellation — there is one procurement act, already structured as
multi-buyer from the start.

**Confirms if:** notice 690422-2026 is the only notice in the candidate's
`signal.notices` list, its 12 buyers plausibly form one joint procurement
(same CPV codes, same title, one winner), and no other TED notice in the
observation window independently names "ex libris" as winner for a buyer in
any of these 5 countries.

**Kills if:** the index or a TED search turns up separate, independently
decided notices — different procedures, different publication numbers not
derived from the same tender — each naming "ex libris" as winner for a buyer
in a different one of the five countries.

## B. Republication artifact: this is the award stage of an already-public
   procedure, not a new event (boring explanation, tested second)

If a contract notice (call for tenders) for the same procurement, same
buyers, same CPV, was already published months earlier, then 690422-2026 is
not new information about an emerging relationship — it is the scheduled,
previously-announced second half (the award result) of a single known
procedure reaching its contractual endpoint.

**Confirms if:** TED holds an earlier `cn-standard` (contract notice) with
the same buyer set, same CPV 72212160, same title, published well before
690422-2026.

**Kills if:** no such prior notice exists, i.e. 690422-2026 is the first
public trace of this procurement.

## C. Genuine finding: an EU-institution-wide Ex Libris dependency is newly
   consolidating

If, contrary to A and B, this notice represents a *new* decision — e.g. a
first-time move of previously separate, nationally-run library systems onto
one shared, single-vendor SaaS platform spanning 12 EU bodies in 5 countries
— that would be a genuine, non-trivial vendor-concentration event worth
tracking (a textbook single-vendor lock-in risk: 8-year term, no
reopening-of-competition framework agreement, €9,000,000 estimated value).

**Confirms if:** no predecessor joint-procurement/framework existed for this
set of buyers for a Library Services Platform, i.e. this is the first
consolidation of these institutions' library systems onto one vendor.

**Kills if:** this merely continues/renews an already-existing joint Ex
Libris/Alma arrangement among (some of) these institutions — in which case
the "family" was already formed, possibly years ago, and today's notice adds
no new concentration.
