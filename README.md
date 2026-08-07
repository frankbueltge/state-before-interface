# state-before-interface

**An autonomous observatory of public AI procurement in Europe.** Working title; V0.

This repository is a running experiment testing one research question:

> What happens when a single machine is built, as consequently as possible, for
> autonomous, public, data-intensive investigation and digital form-making —
> and actually runs the chain
> **signal → candidate → investigation → evidence → verification → form → public result**
> on its own?

It is deliberately **not** part of the research ecology at frankbueltge.de: no
federation, no shared runtime, no personas. Internal agents are ephemeral
capabilities, not characters. The design rationale and the audit that preceded
this code live in [`docs/2026-08-08-audit-und-v0-entwurf.md`](docs/2026-08-08-audit-und-v0-entwurf.md) (German).

## What it observes (V0)

One source: the **TED** (Tenders Electronic Daily) Search API v3 — the EU's
public procurement journal. A nightly, fully deterministic **sentinel** queries
a versioned multilingual envelope of AI-related phrases
([`envelope/queries.json`](envelope/queries.json)), preserves every matching
notice as original bytes (eForms XML) with SHA-256 manifests, and looks for
differences with research value:

| Trigger | Meaning |
|---|---|
| `NEW_MATCH` | a notice enters the envelope for the first time |
| `CHANGED_NOTICE` | preserved bytes of a recent notice changed |
| `DISAPPEARED` | a previously retrievable notice returns 404/410 |
| `PATTERN` | the same vendor wins AI-related contracts in ≥ 2 countries |

Every signal becomes a **case candidate** and passes a six-criteria gate
(observable public problem · machine-readable evidence · potentially
consequential relation · machine-scale advantage · falsifiable investigation ·
possible digital form). Each verdict is committed with per-criterion reasons.
**Most candidates are expected to die** — a committed `DECLINED`, a
`FALSE_ALARM`, an `INSUFFICIENT_EVIDENCE` are successful outcomes, published
like any other. The machine is not optimized for producing works.

Candidates that survive the gate open a **case**. Case mode is an ephemeral
agent run (see [`case_mode/PROMPT.md`](case_mode/PROMPT.md)) that investigates
inside this repository and delivers via pull request: evidence, competing
explanations, an adversarial pass, atomic claims, a terminal state — and, if
the finding warrants it, a public form derived from the structure of the
finding, never from a template gallery.

## Layout

```
envelope/queries.json      the sensor's search envelope, versioned with rationale
snapshots/YYYY-MM-DD/      preserved bytes: search responses, notice XML,
                           manifest.json (URL, UTC retrieval time, SHA-256), run.json
snapshots/index.json       working register of everything seen (derived, git-versioned)
candidates/<id>.json       every signal's gate verdict, OPEN or DECLINED, with reasons
cases/<id>/                state.json, evidence/, analysis/, claims.json, log.jsonl
autonomy/log.jsonl         the autonomy protocol (append-only)
public/                    the generated public page (committed, deterministic)
sentinel/                  the deterministic sentinel (Python, stdlib only)
site/generate.py           builds public/ from committed data, nothing else
verify.py                  walks the provenance chain backwards; CI gate
```

## Invariants

Enforced by `verify.py` and the test suite, not by comments:

- **I1 — unbroken chain:** every published claim → evidence → preserved bytes →
  source URL + UTC retrieval time + SHA-256. `verify.py` fails the build on any hole.
- **I2 — primary sources are irreplaceable:** a model summary may point at
  evidence, never substitute for it.
- **I3 — append-only:** preserved snapshots and closed cases are never edited;
  corrections supersede, they do not overwrite.
- **I4 — no backfill, no invention:** source outages are recorded as outages.
- **I5 — claims are atomic and falsifiable**, separated from evidence.
- **I6 — secrets hygiene:** URLs are stripped of query strings in every error
  path; this archive is public.
- **I7 — null results are published** with the same rank as findings.
- **I8 — no natural persons:** derived data uses an explicit whitelist of
  organization-level fields; contact persons never leave the raw record.

## Autonomy protocol

Autonomy is the research object, so it is measured, not claimed. Every step
appends to `autonomy/log.jsonl`: step, actor (`machine`/`human`), model, tokens,
cost, human interventions, corrections. No aggregate score is computed.

**Standing delegation** (the machine acts without asking): polite retrieval of
public data in the envelope; opening, declining and closing cases in any
terminal state; computing analyses; publishing organization-level facts with
full provenance. **Escalation to the maintainer** (stop before acting):
identifiable natural persons · accusatory framings · any outbound contact
("nothing sends itself") · costs above 20 € per case run or 50 €/month · new
source classes · anything irreversible.

## Operations

- `sentinel.yml` — nightly (05:15 UTC). Runs the sentinel, regenerates
  `public/`, runs `verify.py`, commits as `Observatory
  <observatory@state-before-interface.invalid>`, triggers case mode for newly
  opened candidates.
- `ci.yml` — tests + `verify.py` on every push and PR.
- `case-mode.yml` — the agent run; requires the `ANTHROPIC_API_KEY` secret.
- `deploy.yml` — publishes `public/` to Cloudflare Pages; requires the `CF`
  secret. Both workflows degrade honestly when their secret is missing.

Local:

```bash
cd sentinel && python -m pip install -e '.[dev]' && python -m pytest
python -m sentinel.run --repo-root ..          # a real, live sentinel run
python ../site/generate.py --repo-root ..
python ../verify.py --repo-root ..
```

## Licensing

Code: Apache-2.0 (see `LICENSE`). Own texts: CC BY 4.0. Own derived data
(indexes, manifests, run records): CC0. Preserved TED notices remain documents
of the Publications Office of the European Union and are freely reusable;
source links and retrieval metadata are kept with every copy.
