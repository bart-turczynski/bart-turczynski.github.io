#!/usr/bin/env python3
"""Self-check the redirect site. Exits non-zero on any failure.

Offline checks:
  - every redirects.csv row has its stub file, and the stub's meta refresh,
    rel=canonical, JS location.replace and visible link all equal new_url;
  - each stub is byte-identical to what tools/generate.py would write;
  - match_type is one of same/renamed/section-fallback, and only the package
    root stub may point at a site home;
  - every old page in inventory/<pkg>.txt (old status 200) has a stub, and
    no stub exists without a row;
  - 404.html carries exactly the package -> host map in tools/sites.py, and the
    hand-written index.html links every host; .nojekyll exists.
All site paths are relative to the published directory (docs/).
Online check (skip with --offline): every distinct new_url returns 200 (GET,
redirects followed).

Usage: python3 tools/check.py [--offline]
"""
import csv
import json
import os
import re
import sys
from html import unescape

sys.path.insert(0, os.path.dirname(__file__))
from build_map import is_page, load_inventory, stub_rel  # noqa: E402
from generate import stub_html  # noqa: E402
from http_util import fetch  # noqa: E402
from sites import SITE_DIR, SITES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, SITE_DIR)
KINDS = {"same", "renamed", "section-fallback"}
errors = []


def err(msg):
    errors.append(msg)
    print("FAIL", msg, file=sys.stderr)


def one(pattern, text, what, old):
    found = re.findall(pattern, text)
    if len(found) != 1:
        err(f"{old}: expected one {what}, found {len(found)}")
        return None
    return unescape(found[0])


def main():
    offline = "--offline" in sys.argv[1:]
    with open(os.path.join(ROOT, "redirects.csv")) as fh:
        rows = list(csv.DictReader(fh))
    olds = {r["old_path"] for r in rows}
    if len(olds) != len(rows):
        err("duplicate old_path rows in redirects.csv")

    for r in rows:
        old, url, kind = r["old_path"], r["new_url"], r["match_type"]
        pkg = old.split("/", 1)[0]
        if pkg not in SITES:
            err(f"{old}: unknown package prefix")
            continue
        if kind not in KINDS:
            err(f"{old}: bad match_type {kind!r}")
        if not url.startswith(SITES[pkg]):
            err(f"{old}: target {url} is not on {SITES[pkg]}")
        if url == SITES[pkg] and old != f"{pkg}/index.html":
            err(f"{old}: redirects to the site home")
        path = os.path.join(SITE, old)
        if not os.path.isfile(path):
            err(f"{old}: stub missing")
            continue
        html = open(path).read()
        refresh = one(r'<meta http-equiv="refresh" content="0; url=([^"]*)">', html, "meta refresh", old)
        canon = one(r'<link rel="canonical" href="([^"]*)">', html, "canonical", old)
        js = re.findall(r'location\.replace\(("(?:[^"\\]|\\.)*") \+ location\.hash\)', html)
        js = json.loads(js[0].replace("<\\/", "</")) if len(js) == 1 else err(f"{old}: expected one JS redirect")
        link = one(r'<a href="([^"]*)">', html, "visible link", old)
        for what, got in (("refresh", refresh), ("canonical", canon), ("js", js), ("link", link)):
            if got is not None and got != url:
                err(f"{old}: {what} -> {got}, csv says {url}")
        if html != stub_html(old, url):
            err(f"{old}: stub differs from generator output (run tools/generate.py)")

    for pkg in SITES:  # coverage both ways
        for path, status, _ in load_inventory(pkg):
            if is_page(path) and status == "200" and f"{pkg}/{stub_rel(path)}" not in olds:
                err(f"{pkg}/{path}: old page has no redirect row")
        for d, _, files in os.walk(os.path.join(SITE, pkg)):
            for f in files:
                rel = os.path.relpath(os.path.join(d, f), SITE)
                if rel not in olds:
                    err(f"{rel}: stub without a redirects.csv row")

    nf = open(os.path.join(SITE, "404.html")).read()
    m = re.search(r"var sites = (\{.*?\});", nf, re.S)
    if not m or json.loads(m.group(1)) != SITES:
        err("404.html: package map does not match tools/sites.py")
    idx = open(os.path.join(SITE, "index.html")).read()
    for pkg, url in SITES.items():
        if f'href="{url}"' not in idx:
            err(f"index.html: no link to {url}")
    if not os.path.isfile(os.path.join(SITE, ".nojekyll")):
        err(".nojekyll missing")

    n_ok = 0
    targets = sorted({r["new_url"] for r in rows})
    if not offline:
        for url in targets:
            st, *_ = fetch(url, want_body=False)
            if st == 200:
                n_ok += 1
            else:
                err(f"{url}: HTTP {st}")

    kinds = {k: sum(r["match_type"] == k for r in rows) for k in sorted(KINDS)}
    print(f"rows={len(rows)} {kinds} distinct_targets={len(targets)} "
          f"http200={'skipped' if offline else n_ok} errors={len(errors)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
