# Findings — c-20261003-09

**Signal:** `NEW_MATCH:677429-2026` — notice 677429-2026 (European Commission,
DG CNECT; "AI for Public Good", Lot 1 / Health: AI-based cancer imaging)
entered the envelope on 2026-10-03.

**Proposition tested:** buyer "European Commission, DG CNECT - Communications
Networks, Content and Technology" is already on record (560875-2026) — this
is a sustained procurement programme, not a one-off purchase.

**Terminal state: `INTERESTING_BUT_TRIVIAL`**

## What was tested

Three competing explanations, written before analysis
(`analysis/explanations.md`):

1. **E1 — artifact:** the three DG CNECT notices in the envelope
   (560875-2026, 676246-2026, 677429-2026) double-count one tender split by
   lot, making the "recurring buyer" signal partly spurious.
2. **E2 — genuine:** net of any such artifact, DG CNECT still ran more than
   one independent AI-related procurement procedure.
3. **E3 — trivial:** even if genuine, this is simply expected baseline
   behaviour for a department whose explicit mandate is digital/AI policy,
   not an anomaly worth flagging.

## What survived

Cross-referencing the preserved notice bytes plus one additional publicly
fetched document (the originating contract notice, 115144-2026, retrieved
live from TED and preserved under `evidence/` with manifest) via
`analysis/crossref.py`:

- **E1 confirmed in part:** 676246-2026 and 677429-2026 share
  `ContractFolderID` `f7277ac5-6cb0-4d0a-876d-3e2e5e054bcd` and procedure
  `EC-CNECT/2026/OP/0003`; both are lot-award notices from the single open
  tender published as contract notice 115144-2026 (issued 2026-02-17,
  estimated EUR 5,400,000 across two lots). The naive three-notice count
  overstated distinct procurements by one. **(claim c1)**
- **E2 confirmed, scoped down:** net of that correction, DG CNECT still ran
  a second, fully independent procedure — `EC-CNECT/2025/OP/0095`, the
  public-facing chatbot contract (560875-2026, awarded EUR 149,050) —
  with a different ContractFolderID, different CPV code, and no subject-matter
  overlap with the "AI for Public Good" tender. Two distinct AI-related
  procurement tracks, not three, were observed within the observatory's
  2026-08-07–2026-10-03 window. **(claim c2)**
- **E3 confirmed, nothing irregular found:** no winning organisation appears
  in both procedures' winner lists; both "AI for Public Good" lots were
  awarded at or below their estimated value; procedure type is `open` in
  both cases. The adversarial pass (`analysis/adversarial.md`) also found
  that "sustained programme" overreaches what an 8-week observation window
  can support and restated the claim accordingly (claim c4).

## Why this terminal state

The proposition is **true** (DG CNECT is a recurring, not one-off, AI
procurement buyer in this envelope) and the cross-document linkage — folder
ID matching across three separately-numbered TED notices plus one externally
fetched contract notice — is exactly the kind of connection a human reading
one notice at a time would not make easily. But nothing about the underlying
facts is surprising, irregular, or newsworthy once checked: a department
named "Communications Networks, Content and Technology", which administers
the AI Act and the DSA, running more than one AI-labelled procurement within
a budget period is the expected base rate for that department, not a
pattern. Awards are within estimate, procedures are open and competitive,
and there is no vendor overlap suggesting capture. The most durable output of
this investigation is a bookkeeping correction (three notices → two real
procedures), not a public-interest finding — hence `INTERESTING_BUT_TRIVIAL`
rather than `RESEARCH_RESULT`: the published record is this file plus the
claims/evidence trail, with no derived form.
