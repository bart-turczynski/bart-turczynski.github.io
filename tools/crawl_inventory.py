#!/usr/bin/env python3
"""Enumerate every old URL under https://bart-turczynski.github.io/<pkg>/.

Sources: the old site's sitemap.xml, a BFS crawl of its own HTML links (same-site
only), and a few well-known pkgdown files the sitemap omits. Writes
inventory/<pkg>.txt as "path<TAB>status<TAB>sources" (path relative to the
package prefix, "" = the package root).

Usage: python3 tools/crawl_inventory.py [pkg ...]
"""
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

sys.path.insert(0, os.path.dirname(__file__))
from http_util import fetch  # noqa: E402
from sites import OLD_ORIGIN, SITES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WELL_KNOWN = ["sitemap.xml", "search.json", "pkgdown.yml", "llms.txt", "404.html",
              "news/index.html", "reference/index.html", "articles/index.html",
              "authors.html", "LICENSE.html", "LICENSE-text.html"]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "link", "area"):
            for k, v in attrs:
                if k == "href" and v:
                    self.hrefs.append(v)


def rel_path(url, base):
    """Path of url relative to base (both absolute), or None when off-site."""
    parts = urlsplit(url)
    b = urlsplit(base)
    if parts.scheme not in ("http", "https") or parts.netloc != b.netloc:
        return None
    if not parts.path.startswith(b.path):
        return None
    return parts.path[len(b.path):]


def is_page(path):
    return path == "" or path.endswith("/") or path.endswith(".html")


def crawl(pkg):
    base = f"{OLD_ORIGIN}/{pkg}/"
    found = {}  # path -> set(sources)
    status = {}

    def add(p, src):
        found.setdefault(p, set()).add(src)

    st, _, _, body = fetch(base + "sitemap.xml")
    if st != 200:
        sys.exit(f"{pkg}: sitemap.xml returned {st}")
    for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", body):
        p = rel_path(loc, base)
        if p is not None:
            add(p, "sitemap")
    add("", "root")

    queue = sorted(p for p in found if is_page(p))
    seen = set()
    while queue:
        p = queue.pop(0)
        if p in seen:
            continue
        seen.add(p)
        st, final, ctype, body = fetch(base + p)
        status[p] = st
        if st != 200 or "html" not in ctype:
            continue
        parser = Links()
        parser.feed(body)
        for h in parser.hrefs:
            u = urljoin(final, h.split("#")[0])
            q = rel_path(u, base)
            if q is None or "?" in u:
                continue
            add(q, "crawl")
            if is_page(q) and q not in seen:
                queue.append(q)
        print(f"{pkg}: crawled {p or '/'} ({st})", file=sys.stderr)

    for p in WELL_KNOWN:
        if p not in status:
            st, *_ = fetch(base + p, want_body=False)
            status[p] = st
            if st == 200:
                add(p, "probe")
    # status for non-page crawl finds (assets) not fetched: mark as "-"
    out = os.path.join(ROOT, "inventory", f"{pkg}.txt")
    with open(out, "w") as fh:
        fh.write(f"# old URLs under {base} (path relative to prefix; '' = root)\n")
        fh.write("# path\tstatus\tsources\n")
        for p in sorted(found):
            fh.write(f"{p}\t{status.get(p, '-')}\t{','.join(sorted(found[p]))}\n")
    print(f"{pkg}: {len(found)} paths -> {out}", file=sys.stderr)


if __name__ == "__main__":
    for pkg in sys.argv[1:] or SITES:
        crawl(pkg)
