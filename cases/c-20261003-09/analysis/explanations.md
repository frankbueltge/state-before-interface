# Competing explanations for signal `NEW_MATCH:677429-2026`

Proposition under test: buyer "European Commission, DG CNECT -
Communications Networks, Content and Technology" is already on record
(560875-2026) — i.e. this is a sustained AI procurement programme, not a
one-off purchase.

## E1 — Artifact: the envelope is triple-counting one tender (boring, checked first)

The gate's `machine_scale_advantage` reason fires on raw buyer-name
recurrence across TED publication numbers. DG CNECT has three AI-tagged
notices in the envelope (560875-2026, 676246-2026, 677429-2026). If two of
those three are actually the *same* procurement procedure, split into
separate per-lot award notices by TED's eForms publishing convention, then
counting them as three independent "AI purchases" overstates the buyer's
distinctness and the proposition would be an artifact of notice-splitting,
not of a genuine standing programme.

**What would confirm it:** 676246-2026 and 677429-2026 share the same
`cbc:ContractFolderID` and the same internal procedure reference, and both
cite the same originating contract notice.

**What would kill it:** different `ContractFolderID`/procedure codes, i.e.
genuinely independent procurements that happen to share a title.

**Result: partially confirmed.** `cases/c-20261003-09/analysis/crossref.py`
shows 676246-2026 and 677429-2026 share `ContractFolderID`
`f7277ac5-6cb0-4d0a-876d-3e2e5e054bcd` and procedure `EC-CNECT/2026/OP/0003`,
and both cite contract notice 115144-2026 (same folder, same procedure,
issued 2026-02-17) as their originating tender. They are **one open tender
with two lots, awarded via two separate TED award notices** — not two
independent purchases. The naive 3-notice count overstates distinctness by
one. This does not kill the broader proposition (see E2) but it does correct
it: the true count of *distinct* DG CNECT AI-related procurement procedures
visible in this envelope is **two**, not three.

## E2 — Genuine: DG CNECT runs more than one concurrent/sequential AI-dedicated procurement track

Net of the lot-splitting artifact in E1, is there still a second, genuinely
independent procurement? 560875-2026 carries procedure ID
`EC-CNECT/2025/OP/0095` (public-facing multilingual chatbots for DSA/AI Act
support, awarded EUR 149 050, issued 2026-07-27/2026-08-12). The "AI for
Public Good" tender carries procedure ID `EC-CNECT/2026/OP/0003` (originating
contract notice 2026-02-17, estimated EUR 5 400 000, two lots awarded
2026-09-16/2026-09-30 for a combined EUR 4 772 397.30).

**What would confirm it:** different procedure codes, different years,
different CPV codes, non-overlapping subject matter, overlapping or
sequential timelines (i.e. not a single multi-year framework misread as two).

**What would kill it:** the two procedure IDs turning out to be the same
framework contract drawn down twice, or one of the two "notices" turning out
to be a correction/republication of the other.

**Result: confirmed and not killed.** Procedure IDs differ
(`OP/0095` vs `OP/0003`), CPV differs (72000000 IT services vs 73000000 R&D
services), subject matter differs (chatbot deployment vs AI research
services for cancer imaging and grid optimisation), and the award dates
(Aug 2026 vs Sep/Oct 2026) do not overlap with the earlier contract's
2026-07-27 signature. These are two separate procurement procedures run by
the same buyer unit within roughly a four-month window.

## E3 — Trivial: this is simply expected baseline behaviour for this buyer, not a pattern worth flagging

DG CNECT's explicit mandate covers digital/AI policy (it administers the
Digital Services Act and the AI Act and funds digital-economy research). A
unit with that mandate procuring more than one AI-labelled contract within a
budget year is the expected base rate, not evidence of anything irregular,
disproportionate, or newsworthy. Nothing in the preserved notices shows
non-competitive awards, single-bidder procedures, unusual vendor
concentration, or budget overruns (Lot 1 awarded EUR 2 060 727.30 against an
estimate of EUR 2 400 000 — under estimate; Lot 2 similarly close to
estimate).

**What would confirm it:** awarded amounts within/under estimates, open
procedure type, multiple distinct winners across lots (no single recurring
vendor), no prior adverse signal on this buyer.

**What would kill it:** vendor overlap between the chatbot contract and the
"AI for Public Good" winners, awards exceeding estimates, restricted/
negotiated procedure type, or a pattern of the same small vendor pool
winning repeatedly.

**Result: confirmed.** Procedure type is `open` for both tracks. No vendor
overlap: chatbot winners (NTT Data Belgique, deepset GmbH) share no entity
with Lot 1 winners (FBG, Fundação Champalimaud, FORTH) or Lot 2 winners (AIT,
Areti S.p.A., BIP, INESC TEC, Netz Niederösterreich, a research institute, TU
Denmark, Wiener Netze). Awards are at or under estimate. No irregularity
survives inspection.
