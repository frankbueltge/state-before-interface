import io
import urllib.error

import pytest

from sentinel.fetch import SourceUnavailable, TedClient, redacted


class FakeResponse:
    def __init__(self, data: bytes, status: int = 200):
        self._data = data
        self.status = status

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_redacted_strips_query_and_fragment():
    assert redacted("https://api.example/x/y?key=SECRET&z=1#frag") == \
        "https://api.example/x/y"
    assert redacted("https://api.example/x") == "https://api.example/x"


def test_429_is_retried_then_succeeds():
    calls = {"n": 0}

    def opener(req, timeout):
        calls["n"] += 1
        if calls["n"] < 3:
            raise urllib.error.HTTPError(req.full_url, 429, "too many", {},
                                         io.BytesIO(b""))
        return FakeResponse(b"<xml/>")

    client = TedClient(opener=opener, sleep=lambda s: None, clock=lambda: 0.0)
    data, status = client.fetch_document("https://ted.example/notice/1/xml")
    assert (data, status) == (b"<xml/>", 200)
    assert client.http_429 == 2


def test_non_retriable_status_is_returned_not_raised():
    def opener(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "gone", {},
                                     io.BytesIO(b""))

    client = TedClient(opener=opener, sleep=lambda s: None, clock=lambda: 0.0)
    data, status = client.fetch_document("https://ted.example/notice/1/xml")
    assert (data, status) == (b"", 404)


def test_persistent_failure_raises_redacted_source_unavailable():
    def opener(req, timeout):
        raise urllib.error.URLError("boom")

    client = TedClient(opener=opener, sleep=lambda s: None, clock=lambda: 0.0)
    with pytest.raises(SourceUnavailable) as exc:
        client.fetch_document("https://ted.example/notice/1/xml?token=SECRET")
    assert "SECRET" not in str(exc.value)
    assert "token" not in str(exc.value)
