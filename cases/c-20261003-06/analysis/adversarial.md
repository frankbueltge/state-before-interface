# Adversarial pass — c-20261003-06

Favored explanation going in: E2/E3 combined — this is a real, continuing,
openly published DG CNECT AI procurement activity, not a one-off, but
also not a secret pattern the machine discovered first; it is a routine
institutional output of a unit whose explicit mandate is exactly this.

## Attempt 1 — is the "sustained programme" just full-text bycatch?

The envelope's own rationale (`envelope/queries.json`) warns that `FT=("artificial
intelligence")` picks up bycatch with no CPV filter. If DG CNECT's 27-notice
history were mostly unrelated procurements that happen to mention "artificial
intelligence" once in a boilerplate paragraph, E3 would collapse into "the
phrase is common EU-institutional language" rather than "a programme."

**Test:** read the English titles in the timeline
(`cases/c-20261003-06/analysis/history_output.json`,
`e2_e3_dgcnect_ai_history.timeline`). Result: every one of the 27 titles is
substantively about an AI-named initiative (AI Act technical assistance, AI
Office chatbots, "AI for Public Good", "Digital Twin … AI-powered", "Digital
Transformation Accelerator", an EU-wide AI energy-efficiency study) — none
is a generic IT contract where "AI" appears incidentally.

**Outcome: does not kill E3.** The cluster is thematically coherent, not
full-text noise.

## Attempt 2 — is "AI for Public Good" actually one long-running single
procurement being re-notified, not two editions?

If `EC-CNECT/2024/OP/0094` and `EC-CNECT/2026/OP/0003` turned out to share
a `ContractFolderID` or be corrigenda of the same procedure, "two editions"
would collapse into "one procedure, mis-split by my own project-ID read."

**Test:** compare `cac:ContractFolderID` across `115144-2026.xml` (2026
edition CN) and `484917-2025.xml` (2024/2025 edition CN).
</br>
`115144-2026.xml` → `f7277ac5-6cb0-4d0a-876d-3e2e5e054bcd` (same UUID as the
award `676246-2026.xml`, confirming E1's within-edition link).
`484917-2025.xml` → different UUID (distinct contract folder; see
`cases/c-20261003-06/analysis/history_output.json`, run with
`grep -o 'ContractFolderID>[^<]*' cases/c-20261003-06/evidence/*.xml` for the
raw check — different procurement procedure, different award date, different
estimated amounts: 2024 edition unknown total vs. 2026 edition 5.4M EUR).

**Outcome: does not kill E3.** Two distinct contract folders, two distinct
calls, same title and lot structure a year and a half apart — a recurring
call, not a single re-notified procedure.

## Attempt 3 — negative control: does *every* EU DG show this density, making
it an artifact of how TED indexes big institutions rather than something
specific to DG CNECT's AI mandate?

Not run as a full comparison (out of scope / would need a second source
class of equivalent breadth for a fair baseline), but partially addressed by
the mix of notice types already in hand: of DG CNECT's 27 AI-tagged notices,
12 are contract awards actually completed with named winners and payable
amounts (not just intentions), across at least four distinct thematic lines
(AI Act compliance tooling, DSA chatbots, AI for Public Good, Digital Twin
reconstruction, Digital Transformation Accelerator). A unit that did not
have a standing AI procurement mandate would not show four independent,
completed, multi-hundred-thousand-to-multi-million-euro award lines inside
26 months. This is consistent with, not merely assumed from, the buyer's own
self-description in the notices ("CNECT.A — Artificial Intelligence Office").

**Outcome: survives as a plausibility check, not a controlled negative.**
Flagged here rather than silently treated as confirmed.

## Attempt 4 — retrieval gaps

Two of the 27 historical notices (`763846-2025`, `171702-2026`) returned
persistent `HTTP 202` (TED's on-demand eForms rendering not completing)
across four retries spaced 2–20 s apart on 2026-10-03. Per invariant I4 they
are recorded as an outage, not invented or assumed to say anything in
particular; they are excluded from `evidence/manifest.json` and from any
claim. They do not affect the conclusions above, which rest on the notices
that were successfully retrieved and hashed.

## Net result

E3 (recurring, named, publicly visible "AI for Public Good" programme,
plus a wider multi-year DG CNECT AI procurement stream) survives every
attempt above. Each individual notice was already fully public on TED
before the sentinel's signal fired, so the *existence* of the programme is
not news. What required the machine's cross-notice memory, and is not
visible from any single notice, is: Lot 1 (Health: cancer imaging) failed
to find a winner in the programme's first edition despite 11 submissions,
and the identical lot — same title, same €2.4M estimate — was re-run and
awarded a year later. That specific fact is a legitimate, evidenced,
non-accusatory research result; see `findings.md`.
