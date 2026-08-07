from sentinel import gate
from sentinel import signals as sig


def entry(**overrides):
    base = {
        "first_seen": "2026-08-01",
        "phrases": ["artificial intelligence"],
        "publication_date": "2026-07-30",
        "title": "Germany – AI decision support",
        "titles": ["Germany – AI decision support"],
        "buyer_names": ["Bundesagentur"],
        "buyer_countries": ["DEU"],
        "winner_names": [],
        "vendor_keys": [],
        "cpv": ["72000000"],
        "notice_type": "cn-standard",
        "xml_url": "https://ted.example/1/xml",
        "gone": False,
        "last_checked": "2026-08-01",
        "versions": [{"date": "2026-08-01", "file": "snapshots/2026-08-01/notices/1-2026.xml",
                      "sha256": "ab" * 32}],
    }
    base.update(overrides)
    return base


def test_changed_notice_in_sensitive_domain_opens():
    index = {"1-2026": entry(titles=["Poland – Police analytics platform"])}
    signal = sig.changed_signal("1-2026", "aa" * 32, "bb" * 32, "2026-08-05")
    candidate = gate.evaluate(signal, index)
    assert list(candidate["criteria"]) == list(gate.CRITERIA)
    assert all(c["reason"] for c in candidate["criteria"].values())
    assert candidate["verdict"] == "OPEN"
    assert candidate["proposition"]


def test_bycatch_new_match_is_declined_with_reasons():
    index = {"2-2026": entry(titles=["Norway – Arbitrary waveform generator"],
                             cpv=["34999100"])}
    signal = sig.new_match_signal("2-2026", ["artificial intelligence"], "2026-08-01")
    candidate = gate.evaluate(signal, index)
    assert candidate["verdict"] == "DECLINED"
    assert not candidate["criteria"]["consequential_relation"]["passed"]
    assert not candidate["criteria"]["machine_scale_advantage"]["passed"]
    assert candidate["proposition"] is None


def test_new_match_with_prior_buyer_context_and_sensitive_domain_opens():
    index = {
        "old-2026": entry(first_seen="2026-07-20"),
        "new-2026": entry(first_seen="2026-08-05",
                          titles=["Germany – AI for employment services"]),
    }
    signal = sig.new_match_signal("new-2026", ["artificial intelligence"],
                                  "2026-08-05")
    candidate = gate.evaluate(signal, index)
    assert candidate["criteria"]["machine_scale_advantage"]["passed"]
    assert candidate["verdict"] == "OPEN"


def test_disappeared_and_pattern_pass_machine_scale():
    index = {
        "3-2026": entry(winner_names=["ACME GmbH"], vendor_keys=["acme"],
                        buyer_countries=["DEU"]),
        "4-2026": entry(winner_names=["ACME Ltd"], vendor_keys=["acme"],
                        buyer_countries=["FRA"]),
    }
    patterns = sig.vendor_patterns(index, "2026-08-05", 90)
    assert len(patterns) == 1
    candidate = gate.evaluate(patterns[0], index)
    assert candidate["criteria"]["machine_scale_advantage"]["passed"]
    assert candidate["criteria"]["consequential_relation"]["passed"]
    assert candidate["verdict"] == "OPEN"

    gone = sig.disappeared_signal("3-2026", 404, "2026-08-05")
    candidate = gate.evaluate(gone, index)
    assert candidate["criteria"]["machine_scale_advantage"]["passed"]
