"""HTTP access to TED with throttling, backoff and URL redaction.

Invariant I6: this archive is public, so no query string may ever appear in an
error message or run record — the rule outlives the current (secret-free)
source. Invariant I4: a source outage raises SourceUnavailable and is recorded
as an outage by the caller; nothing is invented.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request

SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
USER_AGENT = "state-before-interface/0.1 (public procurement observatory)"
MIN_INTERVAL_S = 1.2
BACKOFF_S = (30, 60, 120)
RETRIABLE = {429, 500, 502, 503, 504}


def redacted(url: str) -> str:
    """Strip query string and fragment from a URL before it reaches any record."""
    parts = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


class SourceUnavailable(Exception):
    """A source could not be read after retries. Message is already redacted."""

    def __init__(self, url: str, detail: str):
        self.url = redacted(url)
        self.detail = detail
        super().__init__(f"{self.url}: {detail}")


class TedClient:
    """Small, polite TED client. `opener` and `sleep` are injectable for tests."""

    def __init__(self, opener=urllib.request.urlopen, sleep=time.sleep,
                 clock=time.monotonic):
        self._opener = opener
        self._sleep = sleep
        self._clock = clock
        self._last_request_at: float | None = None
        self.requests = 0
        self.http_429 = 0

    def _throttle(self) -> None:
        if self._last_request_at is not None:
            elapsed = self._clock() - self._last_request_at
            if elapsed < MIN_INTERVAL_S:
                self._sleep(MIN_INTERVAL_S - elapsed)
        self._last_request_at = self._clock()

    def _request(self, req: urllib.request.Request) -> tuple[bytes, int]:
        attempts = [0.0, *BACKOFF_S]
        last_detail = "unknown error"
        for i, wait in enumerate(attempts):
            if wait:
                self._sleep(wait)
            self._throttle()
            self.requests += 1
            try:
                with self._opener(req, timeout=60) as resp:
                    return resp.read(), resp.status
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    self.http_429 += 1
                last_detail = f"HTTP {e.code}"
                if e.code not in RETRIABLE:
                    return b"", e.code
            except urllib.error.URLError as e:
                last_detail = f"network error: {getattr(e, 'reason', e).__class__.__name__}"
            except TimeoutError:
                last_detail = "timeout"
        raise SourceUnavailable(req.full_url, f"{last_detail} after {len(attempts)} attempts")

    def search(self, query: str, fields: list[str], limit: int = 50,
               page: int = 1) -> tuple[dict, bytes]:
        """One search page. Returns (parsed, raw bytes) so callers can
        preserve the original response."""
        body = json.dumps({"query": query, "fields": fields,
                           "limit": limit, "page": page}).encode()
        req = urllib.request.Request(
            SEARCH_URL, data=body,
            headers={"Content-Type": "application/json", "User-Agent": USER_AGENT})
        data, status = self._request(req)
        if status != 200:
            raise SourceUnavailable(SEARCH_URL, f"HTTP {status}")
        return json.loads(data), data

    def search_all(self, query: str, fields: list[str],
                   max_pages: int = 10) -> tuple[list[dict], int, bool, list[bytes]]:
        """All notices for a query.
        Returns (notices, total, truncated, raw page responses)."""
        notices: list[dict] = []
        raw_pages: list[bytes] = []
        total = 0
        for page in range(1, max_pages + 1):
            result, raw = self.search(query, fields, page=page)
            raw_pages.append(raw)
            total = result.get("totalNoticeCount", 0)
            batch = result.get("notices") or []
            notices.extend(batch)
            if len(notices) >= total or not batch:
                return notices, total, False, raw_pages
        return notices, total, True, raw_pages

    def fetch_document(self, url: str) -> tuple[bytes, int]:
        """Fetch a single document (e.g. notice XML). Returns (bytes, status)."""
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        return self._request(req)
