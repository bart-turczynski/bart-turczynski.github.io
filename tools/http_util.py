"""Tiny sequential HTTP helper (stdlib only)."""
import time
import urllib.error
import urllib.request

from sites import UA, DELAY


def fetch(url, want_body=True, retries=2):
    """GET url following redirects. Returns (status, final_url, content_type, body_text).

    Network errors (status 0) are retried a couple of times; HTTP errors are not.
    """
    for _ in range(retries):
        res = _fetch_once(url, want_body)
        if res[0] != 0:
            return res
    return _fetch_once(url, want_body)


def _fetch_once(url, want_body):
    time.sleep(DELAY)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read() if want_body else b""
            return (r.status, r.geturl(), r.headers.get("Content-Type", ""),
                    body.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return (e.code, url, e.headers.get("Content-Type", "") if e.headers else "", "")
    except Exception as e:  # network error
        return (0, url, "", repr(e))
