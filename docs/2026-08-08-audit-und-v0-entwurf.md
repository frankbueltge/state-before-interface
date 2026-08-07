# Audit & V0-Entwurf — Autonomes Observatorium öffentlicher KI-Beschaffung

**Datum:** 2026-08-08 · **Status:** Entwurf zur Entscheidung, noch keine Implementierung
**Arbeitstitel (provisorisch, umbenennbar):** `state-before-interface`
**Bezug:** `~/Downloads/letzte-antwort.md` (Forschungsfrage & Konzeptrichtung — als Research
Reference behandelt, alle externen Annahmen neu geprüft)

Die Forschungsfrage, die V0 testen soll:

> Was passiert, wenn eine einzige Maschine maximal konsequent für autonome, öffentliche,
> datenintensive Investigation und digitale Formbildung gebaut wird — und die Kette
> **signal → candidate → investigation → evidence → verification → form → public result**
> tatsächlich selbstständig durchläuft?

Dieses System entsteht **außerhalb der Research Ecology**: keine Federation, kein The Middle,
kein Research Core, keine Ecology-Protokolle als technische Voraussetzung. Wiederverwendet
werden nur erprobte *Muster* (Git-als-Archiv, Provenienz-Disziplin, ehrliche Ausfall-Vermerke),
keine Runtimes.

---

## Teil A — Was real existiert (Workspace-Audit)

Vollinventur am 2026-08-08 (alle Pfade geprüft). Strikt getrennt: **existiert** vs. **vom
Konzeptpapier nur vorgeschlagen**.

### A1. Erprobte Muster, die V0 wiederverwendet (als Muster, nicht als Abhängigkeit)

| Muster | Beleg (real produktiv) | Rolle in V0 |
|---|---|---|
| **Nächtliche Pipeline → Commit → Pages-Rebuild** | 28 Actions-Workflows in `frankbueltge.de/.github/workflows/`; Referenz `protokoll.yml`: Python-Run mit `--dry-run --repo-root .`, dann Commit unter eigener Autor-Identität („Protokollführung"), Push mit Rebase-Retry; Deploy via `deploy-cf.yml` über `workflow_run` (Push mit `GITHUB_TOKEN` löst kein `on: push` aus) | Der komplette Sentinel-Betrieb ist eine Kopie dieses Musters |
| **Rohdaten-Manifest mit SHA-256 je Datei** | `pipelines/newspool/fetch_pool.py` (`manifest.json`); Snapshot-Vertrag mit Hashes auch in `dataset-hub/SNAPSHOT-API.md` | Vorlage für `snapshots/*/manifest.json` |
| **Fetch mit Retry + URL-Redaction** (keine Query-Strings in Fehlermeldungen) | `pipelines/protokoll/src/protokoll/fetch.py` (`_redacted()`), ebenso `pipelines/redaction/src/redaction/cdx.py` | Invariante I6 |
| **„Feststellung entfällt"-Fault-Isolation** (Adapter-Fehler → `status="unavailable"`, nie Crash, nie Erfindung) | `pipelines/protokoll/src/protokoll/adapters/base.py` + `assemble.py` (`build_entry()`) | Invariante I4 |
| **Register-/String-Tests + Drift-Check als CI-Zwang** | `src/lib/**/register.test.ts`, `scripts/drift-check.mjs` (u. a. erzwungene `PALETTE:`-Marker), `drift-watch.yml` | Vorbild für `verify.py` als CI-Gate (I1) |
| **Bot-Identität mit `@<repo>.invalid`-Adresse** | Engine-Commits der Praxen-Repos | Committer des Sentinels |
| **Cloudflare-Pages-Deploy per wrangler aus Actions** | `deploy-cf.yml` (`wrangler pages deploy dist`), inkl. dokumentierter Lehre „genau ein Deployer" (`docs/design/2026-08-03-two-deployers-one-project.md`) | Deploy der öffentlichen Seite |

### A2. Vorhandene Außeninterface-Logik (für V0.1 relevant, nicht V0)

- **Public Seed:** real und mehrstufig — `src/pages/seed/index.astro`, Intake als
  Cloudflare-Pages-Function `functions/api/seed.js` (Honeypot, Ratelimit, Turnstile,
  KI-Gate, KV-Moderations-Queue), Statusrückfluss TAKEN/ADAPTED/DECLINED via
  `scripts/saat/sync.ts`. Das bestätigt: Ein Seed-Eingang als „Sensor unter vielen" ist
  später mit vorhandenem Code-Muster anschließbar.
- **Post Office:** real — Praxen legen `packet.json` in ihren Repos ab,
  `scripts/post/sync-post-ledger.mjs` assembliert den Ledger; hart erzwungen: eine Praxis
  kann nie selbst `sent` setzen. Genau die Semantik, die V0 für Briefe braucht
  („nothing sends itself", Eskalation E-3).

### A3. Meridian — was davon wirklich existiert

Das Konzeptpapier zitiert die Meridian-Runtime als Baustein-Quelle. Befund:

- **Real implementierter Code** (`meridian-runtime/`, eigenes Repo, Python, Tests, zwei
  committete reale Runs): `QuestionModel`, `EvidenceMatrix`, `Evidence Crate`
  (`services/node_runtime/.../evidence_crate.py`), Kill-Condition
  `stop_insufficient_evidence` (`schemas/research-decision.schema.json`, Tests).
- **Nur Spezifikationstext, kein Code:** `DataAssetProfile` (liegt allein im Spec-Dump
  v0.2.0 unter `frankbueltge.de/docs/meridian-research-runtime-spec-v0.2.0/`) und
  `IdentificationAudit` (nur Doku/Task-Packets). Wer diese Konzepte will, baut sie neu.
- Konsequenz wie vom Papier gefordert: **Konzepte übernehmen, Runtime nicht importieren.**
  Die Runtime ist an Postgres/Alembic/Control-Plane gebunden — als Abhängigkeit wäre sie
  sofort „Ecology II".

### A4. dataset-hub

Reale, saubere Infrastruktur (Schema v0.1.0 DCAT-gemappt, Snapshot-Vertrag mit SHA-256,
Ablehnungsregister, Go/No-Go-Messprotokoll je Quelle) — aber **nächtlicher Cron pausiert**
und **Kopplung zur Website bewusst abgebaut**. Für V0 keine Abhängigkeit; das dortige
„Messung vor Adapterbau"-Protokoll ist als Methode übernommen (Teil B ist genau das).

### A5. Was NICHT existiert

Vom vorgeschlagenen System existiert **nichts**: kein Sentinel, keine Case-State-Machine,
kein TED-Adapter, kein Evidence-/Claims-Store, kein Autonomie-Protokoll, keine öffentliche
Oberfläche. Alle Namen in diesem Dokument (Sentinel Mode, Case Mode, Envelope, …) bezeichnen
Zu-Bauendes. Ebenfalls nicht vorhanden: ein Anthropic-API-Key als Actions-Secret in einem
der Repos (die vorhandenen LLM-Pipelines laufen über `GEMINI_API_KEY`); für den Case Mode
ist das eine neue, kleine Einrichtung (Teil D6, Kostengrenze E-4).

---

## Teil B — Externe Annahmen, neu geprüft (Stand 2026-08-08)

Alle Prüfungen heute live durchgeführt (echte API-Calls bzw. aktuelle Quellen), nicht aus der
Doku übernommen. Rohproben liegen im Session-Scratchpad (`ted-sample.xml`).

### B1. TED Search API v3 — **trägt** ✅

| Prüfkriterium | Befund (heute gemessen) |
|---|---|
| Zugang | `POST https://api.ted.europa.eu/v3/notices/search` — **anonym, kein API-Key** für publizierte Notices |
| Format | JSON (Suche); je Notice zusätzlich **eForms-UBL-XML** (strukturiert, ~20 KB, per URL abrufbar) und PDF in 24 Sprachen |
| Abfragesprache | Expert Query (Volltext `FT=…`, Felder wie `buyer-country`, `notice-type`, `classification-cpv`, Datumsbereiche) |
| Historische Tiefe | Abfragen bis mindestens **2016** beantwortet (2 Treffer „artificial intelligence" 2016) |
| Volumen KI-Phrase (EN) | 2018: 52 · 2020: 118 · 2022: 83 · 2023: 96 · 2024: 207 · 2025: 233 · **2026 bis 8.8.: 163** (beschleunigt) |
| Mehrsprachigkeit nötig | „Künstliche Intelligenz" + `buyer-country=DEU` allein: **107 Treffer 2025** — die EN-Phrase sieht nur einen Ausschnitt; der Sensor braucht ein mehrsprachiges Suchfeld |
| Vergabedaten | Award-Notices liefern strukturiert **winner-name, buyer-name, total-value, Währung, CPV** — Vendor-Familien-Analysen sind direkt möglich (55 KI-Award-Notices 2026 bis 8.8.) |
| Kadenz | ~3.250–3.350 neue Notices **pro Werktag** (4 Tage gemessen); KI-Phrase EN: 0–2/Tag — Sentinel-Volumen ist winzig |
| Rate Limit | **Empirisch: HTTP 429** nach ~15–20 schnellen Requests. Nicht dokumentiert → Sentinel braucht Throttling/Backoff (≤ 1 req/s reicht bequem) |
| Lizenz/Reuse | Vergabebekanntmachungen **frei nachnutzbar** (kommerziell und nicht-kommerziell); redaktionelle TED-Inhalte CC BY 4.0; Basis: Kommissionsbeschluss 2011/833/EU |

**Messvorbehalte (ehrlich vermerkt):**
- Der Einbruch 2022/2023 (83/96 Treffer nach 118 im Jahr 2020) fällt mit der
  eForms-Umstellung (Ende 2023) zusammen — plausibel ein **Format-Artefakt der
  Volltextindizierung**, kein realer Beschaffungsrückgang. Vor jeder historischen Aussage
  muss das geklärt werden; bis dahin gilt die Zeitreihe vor 2024 als unkalibriert.
- Volltextsuche produziert **Beifang** (gemessen: ein Signalgenerator-Kauf, der „artificial
  intelligence" nur beiläufig erwähnt). Das ist kein Defekt, sondern der Grund, warum der
  Sentinel ein Relevanz-Gate braucht — und warum `FALSE_ALARM` ein Erfolgs-Endzustand ist.

### B2. EU-AI-Act-Datenbank (Art. 71) — **Annahme gekippt** ❌→⚠️

Die zentrale externe Annahme des Konzeptpapiers hat sich seit dessen Abfassung real geändert:

- Der **Digital Omnibus** verschiebt die Hochrisiko-Pflichten für Annex-III-Systeme —
  **einschließlich der Registrierung in der öffentlichen EU-Datenbank** — von 2026-08-02 auf
  **2027-12-02** (Annex-I-Produkte: 2028-08-02). Politische Einigung 2026-05-07,
  EP-Zustimmung 2026-06-16, Ratsbestätigung 2026-06-29.
- Konsequenz: Die öffentliche Registerseite der Messung „Beschaffung vs. Registrierung"
  bleibt bis Ende 2027 **leer bzw. nicht scharf**. V0 darf **nicht** auf der AI-Act-DB als
  zweitem Register aufbauen.
- Umdeutung statt Streichung: Das **verschobene, leere Register ist selbst Material** —
  exakt die Sorte „missing public record", die das Konzept als materielles Loch beschreibt.
  Die Maschine kann ab Tag 1 dokumentieren, was *später* registrierungspflichtig sein wird
  und heute schon gekauft ist. Wenn die DB 2027 scharf wird, hat das Observatorium die
  Vorher-Baseline, die dann niemand mehr nacherheben kann. **Das macht den Case zeitkritisch
  im umgekehrten Sinn: Der Wert entsteht durch frühes Starten.**

### B3. Weitere Quellen — geprüft

| Quelle | Status heute | Rolle in V0 |
|---|---|---|
| **oeffentlichevergabe.de** (Datenservice Öffentlicher Einkauf) | **Live getestet:** Tagesexport `notice-exports?pubDay=…&format=ocds.zip` → HTTP 200, ~2 MB/Tag, OCDS + eForms-DE + CSV, ohne Registrierung | **Nicht in V0.** Bester Kandidat für die zweite Quelle (nationale Tiefe unterhalb der EU-Schwellen), erst nach bestandenem E2E |
| **PPDS** (Public Procurement Data Space) | Existiert (Launch 2024-09-24), Plattform mit Analytik auf ePO-Ontologie; öffentliches API-Zugangsmodell unklar | **Keine Abhängigkeit.** Referenz, ggf. später prüfen |
| **TED-Bulk/CSV-Historie** (data.europa.eu) | Vorhanden (nicht einzeln verifiziert) | Nicht in V0; Option zur Kalibrierung der Vor-2024-Zeitreihe |
| **Ars-Electronica-Referenz** | Verifiziert: Forensic Architecture, *A Cartography of Genocide*, **Goldene Nica Interactive Art+ 2026**; Jury: „retools the interface as a space of public investigation" | Rahmung/Messlatte, keine technische Annahme |

### B4. Case-Urteil

**„The State Before the Interface" trägt die Forschungsfrage — in korrigierter Form.**

Für den Case sprechen, jetzt empirisch belegt: anonymer maschinenlesbarer Zugang, tägliche
Kadenz, ≥10 Jahre Historie, strukturierte Käufer-/Gewinner-/Wert-Daten, freie Nachnutzung,
beherrschbares Signalvolumen, ein regulatorischer Umbruch, der *während* des Betriebs
stattfindet — und eine Registerlücke, die nur durch frühes kontinuierliches Beobachten
messbar wird. Kein anderer Kandidat aus dem Papier (Permit/Plume, Public Cloud, Moving
Statement) hat einen gleichwertig verifizierten, kostenlosen, legalen Datenzugang **heute**.

Korrektur gegenüber dem Papier: V0 ist **TED-only**. Die Zwei-Register-Messung (Beschaffung
vs. AI-Act-DB) wird zur Baseline-Mission: erst sammeln, ab Dez 2027 vergleichen. Die
Differenz-Messungen, die V0 *sofort* kann, stehen in D3.

---

## Teil C — Minimale Systemgrenze

**Ein Repository. Ein Scheduler. Eine Datenhaltung. Ein öffentlicher Ausgang.** Konkret:

```
INNERHALB der V0-Grenze                      AUSSERHALB (bewusst)
─────────────────────────────                ─────────────────────────────
TED Search API v3 (eine Quelle)              alle weiteren Quellen (DE-OCDS, PPDS, …)
Sentinel: nächtlicher Actions-Run            Dauerbetrieb/Streaming
Case Mode: Agent-Run im Repo                 Multi-Case-Orchestrierung
Append-only-Archiv im Git-Repo               Datenbanken, Objektspeicher, KG
Statische öffentliche Seite                  eigene Domain, Interaktions-Werk
Autonomie-Protokoll (JSONL)                  Metriken-Dashboards
```

Die Grenze ist absichtlich so gezogen, dass **jeder Bestandteil ein bereits erprobtes Muster
aus dem Workspace wiederverwendet** (Teil A) und nichts Neues an Infrastruktur erfunden wird.

---

## Teil D — V0-Entwurf

### D1. Source-of-Truth-Modell

Git ist das Archiv (erprobtes Muster). Alles append-only, Struktur:

```
state-before-interface/
  envelope/queries.json          # das Suchfeld des Sensors, versioniert (mehrsprachige
                                 # Phrasen + CPV-Filter); jede Änderung = Commit mit Grund
  snapshots/YYYY-MM-DD/
    search-response.json         # rohe API-Antwort(en) des Laufs
    notices/<pubnum>.xml         # konservierte eForms-UBL-Originale (die Bytes)
    manifest.json                # je Datei: URL, Abrufzeit UTC, HTTP-Status, SHA-256
  candidates/<id>.json           # CASE_CANDIDATE: Trigger, Signal-Referenzen, Gate-Verdikt
  cases/<id>/
    state.json                   # aktueller Zustand der State Machine + Historie
    evidence/                    # akquirierte Belege (Bytes + Manifest, wie snapshots)
    analysis/                    # Berechnungen: Skripte + Ergebnisse, re-runnable
    claims.json                  # atomare Claims, je mit evidence-Referenzen
    log.jsonl                    # Autonomie-Protokoll (D5)
  public/                        # generierte öffentliche Form (statisch)
```

**Entscheidungsgrundlage Git statt Datenbank:** gemessene Volumina — 0–2 relevante Notices/Tag
à ~20 KB XML plus Manifeste ergeben **< 1 MB/Monat** im Normalbetrieb. Sollte das Suchfeld
wachsen und das Repo real an Grenzen bringen, ist das ein *Befund über die Skalenannahme*,
kein Grund, V0 vorab auf Objektspeicher zu bauen.

### D2. Sentinel→Case-State-Machine

```
                    ┌────────────────────────────────────────────┐
                    │  SENTINEL (nächtlich, deterministisch)     │
                    │  fetch envelope → preserve → hash → diff   │
                    └──────────────┬─────────────────────────────┘
              nichts Neues ────────┤
              (Normalfall,         ▼
               committet   ┌──────────────┐   Trigger-Arten:
               "no signal")│    SIGNAL    │   NEW_MATCH | CHANGED_NOTICE |
                           └──────┬───────┘   DISAPPEARED | PATTERN
                                  ▼
                        ┌──────────────────┐  Gate (alle sechs, maschinell begründet):
                        │  CASE_CANDIDATE  │  öffentl. beobachtbares Problem ∧ genug
                        └──────┬───────────┘  maschinenlesbare Evidenz ∧ potenziell
                     Gate      │              folgenreiche Relation ∧ Maschinen-Skalen-
                     failed ───┤              vorteil ∧ falsifizierbar ∧ digitale Form
                     (DECLINED,▼              möglich
               begründet  ┌──────────┐
               committet) │ CASE_OPEN │ ← ab hier Case Mode (Agent-Run)
                          └────┬─────┘
                               ▼
                  INVESTIGATE: Evidence-Akquise → ≥ 2 konkurrierende
                  Erklärungen → Analyse (re-runnable) → adversariale
                  Gegenprüfung (eigener Schritt, der aktiv zu widerlegen versucht)
                               ▼
        ┌──────────────────────────────────────────────────────────┐
        │ Terminal (alle gleichwertig erfolgreich, alle publiziert):│
        │ FALSE_ALARM · INSUFFICIENT_EVIDENCE · INTERESTING_BUT_    │
        │ TRIVIAL · RESEARCH_RESULT · PUBLIC_WORK · ONGOING_        │
        │ OBSERVATORY                                               │
        └──────────────────────────────────────────────────────────┘
```

Verbindliche Eigenschaften:
- **Der Normalfall ist Stille.** Ein Lauf ohne Signal committet genau das („no signal",
  datiert) — kein Zwang zur Produktion.
- **Die meisten Kandidaten sterben**, und zwar öffentlich begründet. Ein `DECLINED` am Gate
  und ein `FALSE_ALARM` nach Untersuchung sind publizierte Resultate, keine Fehlschläge.
- Sentinel ist **deterministisch** (Regeln: Phrasen-Envelope, CPV-Filter, Diff auf Hashes).
  Ein LLM-Relevanz-Triage vor dem Gate ist V0.1 — erst wenn der gemessene Beifang das
  Gate real verstopft, nicht prophylaktisch.
- Case Mode ist ein **Agent-Run** (LLM mit Werkzeugen) innerhalb des Repos — ephemere
  Capability, keine Persona, kein Name, keine Rolle. Jeder Run ist im Autonomie-Protokoll
  vollständig attribuiert (Modell, Kosten, Schritte).

### D3. Was der Sentinel in V0 konkret misst

Differenzen mit Forschungswert, die TED allein hergibt (alle heute verifizierbar):

1. **Neue KI-Beschaffung** im mehrsprachigen Envelope (Baseline-Mission: das
   Vorher-Register aufbauen, das ab Dez 2027 gegen die AI-Act-DB läuft).
2. **Nachträglich geänderte Notices** (eForms-Change-Notices; Textstände übereinander).
3. **Sprachliche Verwandlung:** dasselbe Vorhaben, das in einem Dokumentstand „AI" heißt
   und in einem anderen nicht mehr — messbar innerhalb von TED über Verfahrens-Referenzen.
4. **Vendor-Familien:** derselbe Gewinner über Länder/Käufer hinweg (winner-name ist
   strukturiert vorhanden; Entity-Resolution nur regelbasiert-konservativ, kein KG).
5. **Verschwinden:** eine Notice, die aus dem Suchergebnis fällt (DISAPPEARED-Trigger).

### D4. Provenienz-/Evidence-Invarianten

Nicht verhandelbare Regeln, als Tests erzwungen (nicht als Kommentare — Kommentare driften):

- **I1 — Kette lückenlos:** Jeder publizierte Claim referenziert Evidence-IDs; jede Evidence
  referenziert konservierte Bytes; jedes konserviertes Artefakt hat Quelle-URL, Abrufzeit
  (UTC) und SHA-256 im Manifest. `original source → retrieval → preserved bytes/hash →
  extraction → analysis → evidence → claim → public form` — ein Skript (`verify.py`) läuft
  die Kette rückwärts und bricht den Build bei jedem Loch.
- **I2 — Primärquelle unersetzbar:** Eine Modellzusammenfassung ist nie Evidence. Sie darf
  auf Evidence zeigen, nie sie ersetzen. Extraktionen tragen `extracted_by` (Regel oder
  Modell+Version) und sind gegen die Bytes nachprüfbar.
- **I3 — Append-only:** Konservierte Snapshots und geschlossene Cases werden nie editiert.
  Korrekturen sind neue, datierte Einträge, die alte **supersehen**, nicht überschreiben.
- **I4 — Kein Backfill:** Kein rückdatierter Eintrag mit heutigen Messwerten. Ausfälle
  werden vermerkt („Feststellung entfällt: <Quelle> <Fehlerklasse>"), nie überbrückt.
- **I5 — Claim/Evidence-Trennung:** `claims.json` enthält atomare, falsifizierbare Aussagen
  mit Konfidenz und Gegenbelegen. Was nicht belegt ist, wird als Schätzung markiert oder
  nicht publiziert.
- **I6 — Secrets-Hygiene:** Fehlermeldungen redigieren Query-Strings; das Archiv ist
  öffentlich, also darf nie ein Key in ein Manifest oder Log geraten (Muster existiert).
- **I7 — Nullresultate publiziert:** FALSE_ALARM / INSUFFICIENT_EVIDENCE /
  INTERESTING_BUT_TRIVIAL erscheinen auf der öffentlichen Seite gleichrangig.
- **I8 — Keine Personen:** V0 verarbeitet und publiziert ausschließlich Organisations- und
  Verfahrensdaten. Namen natürlicher Personen (auch aus öffentlichen Dokumenten, z. B.
  Ansprechpartner in Notices) werden bei Extraktion verworfen.

### D5. Autonomie- und Eskalationsgrenzen

**Autonomie ist Untersuchungsgegenstand, also wird sie gemessen, nicht behauptet.**
Jeder Schritt schreibt ins Autonomie-Protokoll (`log.jsonl`):

```json
{"ts":"…","step":"gate|fetch|analysis|verify|publish|…",
 "actor":"machine|human","model":"<id oder null>","tokens":0,"cost_eur":0.0,
 "human_intervention":null,
 "corrected_by":null}
```

Kein Gesamt-Score. Ausgewertet wird deskriptiv: Welche Schritte liefen autonom, wo griff
ein Mensch ein, was musste korrigiert werden, was hat es gekostet.

**Standing Delegation (die Maschine darf ohne Rückfrage):**
- öffentliche Daten im Envelope höflich abrufen (Throttling, Backoff, User-Agent),
- Kandidaten eröffnen, ablehnen, Cases öffnen und in jeden Terminalzustand schließen,
- Analysen rechnen, Claims formulieren, die öffentliche Seite aktualisieren und
  deployen — solange nur Organisations-/Verfahrensfakten mit lückenloser Provenienz
  publiziert werden,
- das eigene Envelope **vorschlagen** zu ändern (Änderung selbst: siehe Eskalation).

**Eskalation an Frank (Stopp, bevor gehandelt wird):**
- **E-1 Personenbezug:** jede Situation, in der eine natürliche Person identifizierbar würde.
- **E-2 Rechtsrisiko:** jede Formulierung, die einem Akteur Fehlverhalten *vorwirft*
  (Muster/Fakten/Lücken beschreiben ist delegiert; Beschuldigungen nicht).
- **E-3 Kontaktaufnahme:** nichts verlässt das Haus von selbst. Briefe an Behörden/Firmen
  werden als Entwurf committet („nothing sends itself" — gesendet wird auf Franks Knopf).
- **E-4 Kosten:** neue laufende Kosten oder ein Case-Run > 20 € bzw. > 50 €/Monat gesamt
  (Startwerte, justierbar).
- **E-5 Quellen außerhalb des Envelopes:** neue Datenquellen-*Klassen* (Scraping hinter
  Logins, bezahlte Quellen, personenbezogene Register) — öffentliche APIs derselben Klasse
  sind delegiert.
- **E-6 Irreversibles:** alles, was sich nicht durch einen Folge-Commit korrigieren lässt.

Keine täglichen Freigaben. Kein Human Review pro Case. Die Grenze verläuft bei Personen,
Vorwürfen, Kontakt, Geld und Irreversibilität — nicht bei „Qualität".

### D6. Minimales Deploymentmodell

Alle Bausteine sind im Workspace bereits produktiv erprobt (Teil A):

- **Ein öffentliches GitHub-Repo** (Offenheit ist Teil der Beweisführung; Lizenz wie
  Lab-Linie: Apache 2.0 Code / CC BY 4.0 Texte / CC0 Daten).
- **Sentinel:** ein nächtlicher GitHub-Actions-Workflow (Python 3.12, Muster
  Protokoll-Pipeline), committet Snapshots + Diff-Ergebnis als eigene Bot-Identität
  (`…@state-before-interface.invalid`, Muster Engine-Personas — Name generisch, z. B.
  „Observatory", ausdrücklich keine Persona).
- **Case Mode:** Actions-Workflow (`workflow_dispatch` + automatischer Trigger bei
  bestandenem Gate), der einen Agent-Run startet (Anthropic-API-Key als Secret), der im
  Repo arbeitet und per PR/Commit liefert. Kostenlog verpflichtend (D5).
- **Öffentliche Seite:** statischer Build aus `public/` auf Cloudflare Pages
  (Muster deploy-cf.yml; Lehre aus dem Two-Deployer-Problem: **genau eine**
  Deploy-Anbindung). Start unter `*.pages.dev`; Domain ist eine spätere Entscheidung.
- **Kein** Server, keine Datenbank, kein Queue-System, kein Cron außerhalb Actions.

### D7. Erstes E2E-Experiment („E0", 14 Nächte)

**Aufbau:** Envelope v1 = mehrsprachige KI-Phrasen (mindestens EN/DE/FR, gemessen: EN allein
sieht nur einen Ausschnitt) ∪ konservative CPV-Einschränkung; EU-weit; nur TED.

**Ablauf:**
1. Sentinel läuft 14 Nächte autonom (inkl. „no signal"-Nächten).
2. Jedes Signal durchläuft das Gate maschinell; jede Entscheidung wird begründet committet.
3. Mindestens ein Kandidat, der das Gate besteht, durchläuft Case Mode bis zu einem
   Terminalzustand — inklusive adversarialer Gegenprüfung und ohne inhaltlichen
   menschlichen Edit (Eingriffe sind erlaubt, aber sie stehen im Protokoll).
4. Das Terminal-Ergebnis — **auch wenn es FALSE_ALARM ist** — wird als öffentliche Seite
   publiziert, deren Form aus der Struktur des Befunds abgeleitet ist (bei einer
   Textstand-Änderung z. B. übereinandergelegte Fassungen; bei einem Fehlalarm die
   Anatomie des Fehlalarms). Keine generische Karte, kein Dashboard.
5. `verify.py` läuft als CI-Gate über alles Publizierte.

**Was E0 beantwortet:** ob die Kette real autonom durchläuft, wo sie reißt, was Autonomie
kostet, und ob aus einem echten (auch negativen) Befund eine notwendige Form entsteht.

### D8. Bewusst nicht gebaut (V0)

Microservices · universelle Agentenframeworks · allgemeine Ontologien · Knowledge-Graph ·
Dashboards · generische Workflow-Builder · Multi-Case-Orchestrierung · Ecology-Integration
(keine Federation, kein The Middle, keine Encounters-Pflicht) · Personas/Rollen/Kollektive ·
AI-Act-DB-Anbindung (bis die DB real befüllt ist) · PPDS-Anbindung · zweite Datenquelle
(DE-OCDS wartet auf bestandenes E0) · Seed-Eingang und Post-Office-Ausgang (Außeninterfaces
ab V0.1 — als Signalklasse bzw. Entwurfs-Ordner bereits im Datenmodell vorgesehen, aber ohne
UI) · LLM-Triage im Sentinel (erst bei realem Beifang-Problem) · eigene Domain · Backfill.

### D9. Acceptance Criteria — wann testet V0 die Forschungsfrage wirklich?

V0 gilt als gültiger Test, wenn nach E0 **alle** folgenden Punkte belegt sind:

- **A1 — Kette:** Mindestens ein Durchlauf signal → candidate → investigation → evidence →
  verification → form → public result ist vollständig dokumentiert; jeder menschliche
  Eingriff steht im Autonomie-Protokoll (Ziel ist nicht null Eingriffe, sondern **gemessene**
  Eingriffe).
- **A2 — Provenienz:** `verify.py` läuft grün über alles Publizierte; Stichprobe von Hand:
  von jedem Claim in ≤ 3 Klicks zu konservierten Originalbytes.
- **A3 — Legitimes Sterben:** Mindestens ein Kandidat endet öffentlich in FALSE_ALARM,
  INSUFFICIENT_EVIDENCE oder INTERESTING_BUT_TRIVIAL — mit nachvollziehbarer Begründung.
- **A4 — Entdeckung:** Mindestens ein Signal stammt aus dem Diff der Maschine, nicht aus
  einem menschlichen Hinweis („not in its prompt").
- **A5 — Autonomie messbar:** Für jeden Schritt ist ablesbar: Akteur, Modell, Kosten,
  Korrekturen. Eine deskriptive Auswertung (keine Scores) liegt vor.
- **A6 — Form aus Befund:** Die publizierte Form ist aus der Struktur des konkreten Befunds
  begründet (dokumentierte Ableitung), nicht aus einer Template-Galerie.
- **A7 — Reproduzierbarkeit:** Eine dritte Person kann mit Repo-Inhalt allein die Analyse
  eines abgeschlossenen Cases erneut ausführen und kommt zum selben Ergebnis.

Scheitert E0 an einem Kriterium, ist das selbst ein publizierbares Resultat über die
Forschungsfrage — der Apparat wird nicht zur Werkproduktion optimiert.

---

## Teil E — Offene Entscheidungen (Frank)

1. **Name:** `state-before-interface` ist Arbeitstitel (Case-Name als Repo-Name passt zur
   Ein-Case-Disziplin von V0); Umbenennen ist trivial, solange nichts publiziert ist.
2. **Öffentlich ab Tag 1?** Entwurf sagt ja (Provenienz-Argument). Alternative: privat bis
   E0 bestanden, dann Historie offenlegen.
3. **Kostenrahmen:** Startwerte in E-4 (20 €/Case-Run, 50 €/Monat) bestätigen oder ändern.
4. **Sprache des Repos:** Vorschlag Englisch (wie Ecology-Repos, aber eigene Entscheidung —
   die EN-only-Regel der Ecology bindet dieses Projekt nicht automatisch).
5. **Startzeitpunkt E0:** Nach Zustimmung zu diesem Entwurf; Implementierungsaufwand des
   Slices ist bewusst klein gehalten.
