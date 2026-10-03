# Adversarial pass

Target: the favoured explanation (E2 in `explanations.md`) — DG CNECT runs
two genuinely distinct AI procurement procedures within the observed window,
so the "sustained programme, not a one-off" proposition holds (corrected to
"two", not three, distinct procedures per E1).

## Attempt 1 — are 676246-2026 and 677429-2026 actually the same notice (duplicate/corrigendum), not two lots?

Checked lot identifiers inside each preserved XML: 677429-2026 carries only
`LOT-0001`, 676246-2026 carries only `LOT-0002` (`grep -n "LOT-000"` on both
files, see command output captured during investigation). Winner lists are
disjoint (FBG/Fundação Champalimaud/FORTH vs AIT/Areti/BIP/INESC
TEC/NETZ Niederösterreich/Wiener Netze/a research institute/TU Denmark).
**Outcome: survives.** These are two distinct lot-award notices, not a
duplicate pair.

## Attempt 2 — is the "sustained programme" claim actually just the observatory's short memory mistaking a single long-running framework for two independent initiatives?

Checked `ContractFolderID` and internal procedure code for 560875-2026
(`b74a2278-5248-42c0-93db-74fc0127ab93`, `EC-CNECT/2025/OP/0095`) against the
"AI for Public Good" family (`f7277ac5-6cb0-4d0a-876d-3e2e5e054bcd`,
`EC-CNECT/2026/OP/0003`). Folder IDs and procedure codes differ completely;
CPV differs (72000000 vs 73000000); subject matter differs (chatbot
deployment vs AI research services). **Outcome: survives.** These are not
the same framework re-surfacing.

## Attempt 3 — does "sustained" overclaim beyond what the evidence supports?

The observatory's envelope has only run since 2026-08-07 (`envelope/queries.json`,
version 1, `as_of: 2026-08-08`) through 2026-10-03 — an 8-week window. Two
distinct procedures observed inside an 8-week window is a real finding, but
"sustained procurement programme" could be read as implying a multi-year
pattern this observatory cannot see. No pre-August-2026 TED search was run
to check for earlier DG CNECT AI notices — doing so would mean issuing a
query outside the committed, versioned envelope, which this run did not do
in order to stay inside the designed scope of one case investigation.
**Outcome: claim weakened, not killed.** The finding is restated as: DG CNECT
ran at least two independent, non-overlapping AI-procurement procedures
within the observatory's 8-week observation window (2026-08-07 to
2026-10-03) — a lower bar than "sustained programme" but a claim the
evidence fully supports, with the window explicitly disclosed as a limit.

## Attempt 4 — negative control: does the same cross-reference method produce a false "programme" for an unrelated single-notice buyer?

Spot-checked that the `machine_scale_advantage` method (shared
`ContractFolderID`) is required, not just shared buyer name, before counting
two notices as "one procedure". Applying the same test to 560875-2026 alone
(no sibling notice shares its folder ID in the preserved index) correctly
yields a count of one, not an inflated count — i.e. the method does not
manufacture programmes where there is only one notice. **Outcome: survives**
(no false positive on the control case).
