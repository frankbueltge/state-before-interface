#!/usr/bin/env python3
"""Build public/ deterministically from committed records — nothing else.

The page is the observatory's public register: envelope, runs (including
"no signal" nights), every candidate with its verdict and reasons, every case
with its state. Null results rank equal to findings (invariant I7). Case forms
(cases/<id>/form/) are copied verbatim; their shape belongs to the finding.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

TERMINALS = ("FALSE_ALARM", "INSUFFICIENT_EVIDENCE", "INTERESTING_BUT_TRIVIAL",
             "RESEARCH_RESULT", "PUBLIC_WORK", "ONGOING_OBSERVATORY")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def _candidate_summary(candidate: dict) -> str:
    if candidate["verdict"] == "OPEN":
        return candidate.get("proposition") or ""
    failed = [c["reason"] for c in candidate["criteria"].values()
              if not c["passed"]]
    return " · ".join(failed)


def build(root: Path, out: Path | None = None) -> Path:
    out = out or root / "public"
    envelope = read_json(root / "envelope" / "queries.json", {})
    index = read_json(root / "snapshots" / "index.json",
                      {"notices": {}, "emitted": []})
    runs = [read_json(p) for p in sorted(root.glob("snapshots/*/run.json"))]
    candidates = [read_json(p) for p in sorted(root.glob("candidates/*.json"))]
    cases = {p.parent.name: read_json(p)
             for p in sorted(root.glob("cases/*/state.json"))}
    repo_url = read_json(root / "site" / "config.json", {}).get("repo_url", "")

    def repo_link(rel: str, label: str) -> str:
        if not repo_url:
            return esc(label)
        return f'<a href="{esc(repo_url)}/blob/main/{esc(rel)}">{esc(label)}</a>'

    as_of = runs[-1]["date"] if runs else envelope.get("as_of", "")
    n_open = sum(1 for c in candidates if c["verdict"] == "OPEN")
    n_declined = len(candidates) - n_open

    parts: list[str] = []
    parts.append(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>state before interface — an autonomous observatory of public AI procurement</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header>
<h1>STATE BEFORE THE INTERFACE</h1>
<p class="sub">An autonomous observatory of public AI procurement in Europe.
Working state V0 · observations as of <strong>{esc(as_of)}</strong></p>
<p class="question">One machine runs the chain
<code>signal → candidate → investigation → evidence → verification → form →
public result</code> on its own. Autonomy is the research object: every step is
attributed, every intervention logged. Most candidates are expected to die —
a published <em>false alarm</em> is a successful outcome, not a failure.</p>
</header>
<main>""")

    parts.append(f"""
<section>
<h2>Observed so far</h2>
<ul class="stats">
<li><strong>{len(index["notices"])}</strong> notices preserved</li>
<li><strong>{sum(len(r.get("signals", [])) for r in runs)}</strong> signals</li>
<li><strong>{n_open}</strong> candidates opened</li>
<li><strong>{n_declined}</strong> candidates declined</li>
<li><strong>{len(cases)}</strong> cases</li>
</ul>
</section>""")

    phrases = "".join(
        f"<li><code>{esc(p['text'])}</code> <span class=lang>({esc(p['lang'])})</span></li>"
        for p in envelope.get("phrases", []))
    parts.append(f"""
<section>
<h2>The envelope</h2>
<p>The sentinel queries the TED Search API nightly for these exact phrases
(envelope v{esc(envelope.get('version', '?'))}, every change is a committed
revision with a reason):</p>
<ul class="phrases">{phrases}</ul>
<details><summary>Why no CPV filter?</summary>
<p>{esc(envelope.get('rationale', ''))}</p></details>
</section>""")

    if runs:
        rows = "".join(
            f"<tr><td>{esc(r['date'])}</td>"
            f"<td>{esc(len(r.get('new_matches', [])))}</td>"
            f"<td>{esc(r.get('rechecked', 0))}</td>"
            f"<td>{esc(len(r.get('signals', []))) if r.get('signals') else 'no signal'}</td>"
            f"<td>{esc(len(r['candidates']['open']))}</td>"
            f"<td>{esc(len(r['candidates']['declined']))}</td>"
            f"<td>{esc(len(r.get('failures', [])))}</td></tr>"
            for r in reversed(runs))
        parts.append(f"""
<section>
<h2>Runs</h2>
<div class="scroll"><table>
<thead><tr><th>night</th><th>new</th><th>rechecked</th><th>signals</th>
<th>opened</th><th>declined</th><th>outages</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p class="note">A night without signal is the normal case and is committed as
exactly that. Source outages are recorded, never bridged.</p>
</section>""")

    if candidates:
        items = []
        for c in reversed(candidates):
            notices = ", ".join(
                repo_link(v["file"], p)
                for p in c["signal"]["notices"][:6]
                for v in [index["notices"].get(p, {}).get("versions", [{}])[0]]
                if v.get("file"))
            items.append(f"""
<article class="candidate {esc(c['verdict']).lower()}">
<h3>{repo_link(f"candidates/{c['id']}.json", c['id'])}
<span class="badge {esc(c['verdict']).lower()}">{esc(c['verdict'])}</span>
<span class="type">{esc(c['signal']['type'])}</span></h3>
<p>{esc(c['signal']['detail'])}</p>
<p class="reasons">{esc(_candidate_summary(c))}</p>
<p class="notices">record(s): {notices or '—'}</p>
</article>""")
        parts.append(f"""
<section>
<h2>Candidates</h2>
<p>Every signal faces six criteria; each verdict is committed with
per-criterion reasons. Declined candidates stay on record.</p>
{''.join(items)}
</section>""")

    if cases:
        items = []
        for cid, state in sorted(cases.items(), reverse=True):
            form_link = ""
            if (root / "cases" / cid / "form" / "index.html").exists():
                form_link = f' · <a href="cases/{esc(cid)}/">public form</a>'
            items.append(
                f"<li>{repo_link(f'cases/{cid}/state.json', cid)} — "
                f"<span class='state'>{esc(state['state'])}</span>{form_link}</li>")
        parts.append(f"""
<section>
<h2>Cases</h2>
<ul class="cases">{''.join(items)}</ul>
<p class="note">Terminal states: {esc(' · '.join(TERMINALS))} — all of equal
rank, all published.</p>
</section>""")

    verify_cmd = "python verify.py --repo-root ."
    parts.append(f"""
</main>
<footer>
<p>Every figure on this page is derived from committed records; the page is
rebuilt deterministically from the repository and from nothing else. Verify the
chain yourself: <code>{esc(verify_cmd)}</code>{' in <a href="' + esc(repo_url) + '">the repository</a>' if repo_url else ''}.
Preserved notices remain documents of the Publications Office of the European
Union (freely reusable); retrieval time and SHA-256 are kept with every copy.
Derived data: CC0. Texts: CC BY 4.0. Code: Apache-2.0.</p>
<p>No natural persons: derived data carries organization-level fields only.
Nothing sends itself: any outbound letter would be prepared as a draft and
dispatched only by a human hand.</p>
</footer>
</body>
</html>
""")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "index.html").write_text("".join(parts), encoding="utf-8")
    (out / "style.css").write_text(STYLE, encoding="utf-8")
    for form in sorted(root.glob("cases/*/form")):
        if (form / "index.html").exists():
            shutil.copytree(form, out / "cases" / form.parent.name)
    return out


STYLE = """\
:root {
  color-scheme: light dark;
  --bg: #faf9f6; --fg: #1c1c1a; --muted: #6b6a64; --line: #e2e0d8;
  --open: #0a6b3d; --open-bg: #e3f2e9; --declined: #7a4a12; --declined-bg: #f6ead9;
  --accent: #1a4f8a;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16161a; --fg: #e8e6e0; --muted: #9a988f; --line: #32323a;
    --open: #6fce9e; --open-bg: #10301f; --declined: #e0a86a; --declined-bg: #33240f;
    --accent: #7aaede;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0 auto; padding: 2rem 1rem 4rem; max-width: 46rem;
  background: var(--bg); color: var(--fg);
  font: 1rem/1.55 ui-sans-serif, system-ui, sans-serif;
}
header h1 { font-size: 1.4rem; letter-spacing: 0.14em; margin: 0 0 0.4rem; }
.sub { color: var(--muted); margin: 0 0 1rem; }
.question { border-left: 3px solid var(--accent); padding-left: 0.8rem; }
h2 { font-size: 1.05rem; margin: 2.2rem 0 0.6rem; letter-spacing: 0.04em; }
h3 { font-size: 0.95rem; margin: 0 0 0.3rem; }
a { color: var(--accent); }
code { font-family: ui-monospace, monospace; font-size: 0.9em; }
.stats { list-style: none; padding: 0; display: flex; flex-wrap: wrap; gap: 0.5rem 1.4rem; }
.phrases { list-style: none; padding: 0; }
.lang { color: var(--muted); }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.9rem; }
th, td { text-align: left; padding: 0.3rem 0.7rem 0.3rem 0; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; }
.candidate { border: 1px solid var(--line); border-radius: 6px; padding: 0.7rem 0.9rem; margin: 0.7rem 0; }
.badge { font-size: 0.72rem; padding: 0.1rem 0.45rem; border-radius: 99px; vertical-align: middle; letter-spacing: 0.06em; }
.badge.open { background: var(--open-bg); color: var(--open); }
.badge.declined { background: var(--declined-bg); color: var(--declined); }
.type { color: var(--muted); font-size: 0.78rem; margin-left: 0.4rem; }
.reasons, .notices, .note { color: var(--muted); font-size: 0.88rem; }
.cases { list-style: none; padding: 0; }
.state { letter-spacing: 0.05em; font-size: 0.85rem; }
footer { margin-top: 3rem; border-top: 1px solid var(--line); padding-top: 1rem;
         color: var(--muted); font-size: 0.85rem; }
details summary { cursor: pointer; color: var(--accent); }
@media (prefers-reduced-motion: reduce) { * { scroll-behavior: auto; } }
"""


def main(argv=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)
    out = build(args.repo_root.resolve(), args.out)
    print(f"public page written to {out}")


if __name__ == "__main__":
    main()
