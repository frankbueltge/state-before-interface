# Kandidat: Der Nachrichten-Schatten der Beschaffung (TED × GDELT)

**Status:** Exposé zur Mitnahme in eine eigene Session · 2026-08-09
**Kontext:** Entstanden aus der GDELT-Lebendigkeits-Prüfung vom 2026-08-09 in der
frankbueltge.de-Session (Feeds, BigQuery und Blog erstgeprüft, alle live). Angeboten als
Kandidat, nicht als Auftrag — das Observatorium entscheidet in eigener Session. Die
USP-Pflicht vom 2026-08-09 gilt: vor einem Go gehört der Nachbarn-Check ins Protokoll.

## Einzeiler

Die Maschine hält den Verwaltungsakt (TED: jede europäische KI-Beschaffung) gegen sein
Medienecho (GDELT: 65 Sprachen, 15-Minuten-Takt) — und misst kontinuierlich, welche
Beschaffungen öffentlich werden, wo, mit welchem Ton, und welche für immer unterhalb
der Nachrichtenschwelle bleiben.

## Forschungsfrage

Der Staat kauft KI im Amtsblatt, nicht in der Zeitung: Welcher Anteil der europäischen
KI-Beschaffungen erreicht je ein Nachrichtenmedium — in welchem Land, in welcher Sprache,
mit welcher Verzögerung und welchem Ton — und was kennzeichnet die Beschaffungen, die
*nie* Nachricht werden? Der Nicht-Schatten ist der Befund: „the state before the
interface", auf die Medienöffentlichkeit übertragen.

## Maschinen-Überlegenheit

- Beide Quellen ticken kontinuierlich (TED täglich, GDELT alle 15 Minuten); die Kreuzung
  ist nur als stehende Beobachtung sinnvoll — kein Mensch hält sie.
- 65-Sprachen-Abdeckung: ob eine rumänische Vergabe in Rumänien Nachricht wurde, liest
  keine englischsprachige Redaktion nach.
- Die Verknüpfung ist prüfbar: jede Behauptung trägt die TED-Notice-ID und die
  GDELT-Artikel-URLs; „kein Echo gefunden" ist als durchsuchter Zeitraum + Suchraum
  dokumentierbar, nicht als Behauptung.

## Datenlage (Kurzcheck 2026-08-09, erstgeprüft in der Nacht-Session)

- GDELT-v2-Rohfeeds: aktuell bis auf den laufenden 15-Minuten-Zyklus
  (`lastupdate.txt`, geprüft 22:36 UTC gegen Datei 22:45).
- BigQuery `gdelt-bq.gdeltv2.events`: zuletzt geändert 22:33 UTC am Prüftag,
  905 970 738 Zeilen; `gkg_partitioned` gleicher Stand. Public Dataset, Abfragen im
  1-TB/Monat-Freikontingent möglich; GCP-Projekt vorhanden.
- TED Search API v3: bereits die Ein-Quellen-Basis des Observatoriums (Sentinel läuft).
- Bekannte Schwäche, ehrlich: GDELTs eigene Doku ist seit ~2016 eingefroren; die
  Abdeckungs-Verzerrungen des Instruments müssten als Limitation ins Methodenblatt
  (kleine Medien, Paywalls, Nicht-Nachrichten-Öffentlichkeit wie Fachblogs).

## Nachbarn (Startpunkte für den Pflicht-Check, nicht abschließend)

- OpenTender / DIGIWHIST: Beschaffungs-Transparenz, kein Medienabgleich.
- AlgorithmWatch „Automating Society" u. ä.: kuratierte Fallberichte, keine stehende
  Messung. — Der kontinuierliche TED×GDELT-Abgleich selbst ist beim Kurzcheck ohne
  Treffer; der volle Nachbarn-Check steht aus.
