# Adversarial pass — c-20261007-05

Goal: try to destroy explanation A ("one joint-procurement notice, not five
relationships") and explanation B ("republication of an already-public
procedure"), since both are the favored, case-killing readings.

## Attack 1 — maybe the 12 buyers are not really one joint contract

If the notice bundled 12 unrelated lots (one per buyer/country) that each
went to "ex libris" independently, the five-country spread would still
reflect 12 separate decisions, just republished together — closer to a real
constellation.

Checked directly against the preserved XML (`snapshots/2026-10-07/notices/690422-2026.xml`,
see `analysis/inspect_notice.py` output): exactly one
`<cac:ProcurementProjectLot>`, one `<efac:LotResult>`, one winner name ("EX
LIBRIS"), one framework-agreement type (`fa-wo-rc`, no reopening of
competition), one estimated value (€9,000,000) and one duration (96 months).
The 12 buyer `CompanyID`s (AMLA, CONSIL, COR, CURIA, ECA, EEAS, EESC, EP,
EUAA, EUCOM, EUDA, EURSCHOOL, PUBL) are co-contracting authorities on that
single lot, not 12 separate procurements.

**Outcome: attack fails.** It is one award, confirmed at the byte level, not
twelve bundled ones.

## Attack 2 — maybe 57057-2026 is an unrelated notice that happens to share
   a title

Titles can collide (templated TED titles are often auto-generated from buyer
+ CPV and could repeat for different procedures).

Checked: fetched the TED search API record for `publication-number=57057-2026`
(`cases/c-20261007-05/evidence/57057-2026-search.json`) and for
`classification-cpv=72212160 AND buyer-name="European Parliament"`
(`cases/c-20261007-05/evidence/european-parliament-library-cpv-search.json`,
reproduced in `analysis/check_pattern.py` output). 57057-2026 is a
`cn-standard` (contract notice) published 2026-01-26 naming the *identical*
12 buyers, in the same order, under the same CPV 72212160, with the
identical multilingual title set as 690422-2026. TED's own CPV+buyer query
returns exactly these two notices for this buyer across all years — no third
candidate procedure to confuse them with.

**Outcome: attack fails.** Same procedure, two publication stages
(call-for-tenders in January, award eight months later), not two
coincidentally similar ones.

## Attack 3 — negative control: does the same detector logic produce a
   false "no pattern" on a case that should have one?

Queried TED for every notice where `winner-name="ex libris"` and
`classification-cpv=72212160` (`cases/c-20261007-05/evidence/ex-libris-library-cpv-search.json`).
Three notices total, worldwide, in TED's current index: Italy (South
Tyrol, 2024), Netherlands (2025), and this one (2026). Only the 2026 notice
has more than one buyer country. If "ex libris" had a real, separate,
expanding footprint across many independent public buyers, this query
should show it; it does not — two single-country notices and one
multi-buyer joint one.

**Outcome: control behaves as expected** — no hidden broader constellation
is being missed by the narrower checks above; the signal really is
carried by this one notice alone.

## Attack 4 — is the underlying "AI procurement" framing itself solid?

Checked how many times the envelope phrase "artificial intelligence" occurs
in the notice body (`analysis/inspect_notice.py`): once, inside the postal
address block of the Publications Office contact, as part of the name of
their internal unit ("OP.A ... and Artificial Intelligence Exploitation").
The procured product (a Library Services Platform / resource discovery
service) is not described anywhere in the document as AI-related.

**Outcome:** this strengthens, not weakens, the case-killing reading — the
notice entered the observatory's AI envelope as bycatch (a department name),
a known and accepted cost of the phrase-only envelope (see
`envelope/queries.json` rationale: "Bycatch is expected and is handled by
the gate, not the envelope").

## What survived

Explanations A and B both survived every attempted attack and are mutually
reinforcing: one framework-agreement award notice, already previewed by a
contract notice eight months earlier, entered the AI envelope only because
of an unrelated department name. Explanation C (a genuine new
multi-institution AI-vendor concentration) is not supported: there is no
second, independent decision point — only one procedure with one outcome,
and the "AI" link that justified the candidate's priority is itself a
false lead.
