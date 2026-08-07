from sentinel.extract import (FIELD_WHITELIST, names, normalize_vendor, slim,
                              title_display, titles)


def test_slim_drops_everything_outside_the_whitelist():
    raw = {
        "publication-number": "1-2026",
        "notice-title": {"eng": "AI platform"},
        "links": {"xml": {"MUL": "https://example.invalid/xml"}},
        "contact-name": "Jane Doe",
        "organisation-contact-point": {"eng": ["John Smith"]},
    }
    slimmed = slim(raw)
    assert set(slimmed) <= set(FIELD_WHITELIST)
    assert "links" not in slimmed
    assert "contact-name" not in slimmed
    assert "organisation-contact-point" not in slimmed


def test_names_flattens_multilingual_dicts():
    assert names({"hrv": ["A d.o.o.", "B d.o.o."], "eng": ["A d.o.o."]}) == \
        ["A d.o.o.", "B d.o.o."]
    assert names(["DEU", "FRA"]) == ["DEU", "FRA"]
    assert names(None) == []


def test_titles_and_display_prefer_english():
    field = {"deu": "Deutschland – KI", "eng": "Germany – AI"}
    assert title_display(field) == "Germany – AI"
    assert titles(field) == ["Deutschland – KI", "Germany – AI"]


def test_normalize_vendor_strips_legal_suffixes():
    assert normalize_vendor("CS Computer Systems d.o.o.") == "cs computer systems"
    assert normalize_vendor("Danish Centre for AI Innovation A/S") == \
        "danish centre for ai innovation"
    assert normalize_vendor("Keysight Technologies Deutschland GmbH") == \
        "keysight technologies deutschland"
    assert normalize_vendor("ACME") == normalize_vendor("acme ltd")
