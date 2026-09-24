#!/usr/bin/env python3
"""Map every old page in inventory/<pkg>.txt to its equivalent on the canonical host.

For each old page (old status 200; the root, a directory, or a .html file):
  1. same     - the same relative path on the new host returns 200 (GET, redirects followed);
  2. renamed / section-fallback - an explicit row in tools/overrides.csv, verified 200.
Anything else is a hard error: no silent fallback to a site home.

Writes redirects.csv (old_path,new_url,match_type) and inventory/unstubbed.csv
(inventory entries that get no stub, with the reason).

Usage: python3 tools/build_map.py
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from http_util import fetch  # noqa: E402
from sites import SITES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def is_page(p):
    return p == "" or p.endswith("/") or p.endswith(".html")


def stub_rel(p):
    """Old path -> file path of its stub (relative to the package prefix)."""
    return p + "index.html" if p == "" or p.endswith("/") else p


def target_rel(stub):
    """Stub file -> preferred target path: index pages point at their directory."""
    if stub == "index.html":
        return ""
    if stub.endswith("/index.html"):
        return stub[: -len("index.html")]
    return stub


def load_inventory(pkg):
    rows = []
    with open(os.path.join(ROOT, "inventory", f"{pkg}.txt")) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip("\n"):
                continue
            path, status, sources = line.rstrip("\n").split("\t")
            rows.append((path, status, sources))
    return rows


def main():
    overrides = {}
    with open(os.path.join(ROOT, "tools", "overrides.csv")) as fh:
        for r in csv.DictReader(fh):
            overrides[(r["pkg"], r["old_path"])] = r

    redirects, unstubbed, unresolved = [], [], []
    for pkg, new_root in SITES.items():
        stubs = {}
        for path, status, _ in load_inventory(pkg):
            if not is_page(path):
                reason = "junk-link" if not os.path.splitext(path)[1] else "non-html"
                unstubbed.append((f"{pkg}/{path}", reason))
                continue
            if status != "200":
                unstubbed.append((f"{pkg}/{path}", f"old-{status}"))
                continue
            stubs.setdefault(stub_rel(path), path)
        for stub in sorted(stubs):
            ov = overrides.get((pkg, stub))
            if ov:
                rel, kind = ov["new_rel"], ov["match_type"]
            else:
                rel, kind = target_rel(stub), "same"
            url = new_root + rel
            st, *_ = fetch(url, want_body=False)
            print(f"{st} {kind:16} {pkg}/{stub} -> {url}", file=sys.stderr)
            if st != 200:
                unresolved.append((f"{pkg}/{stub}", url, st))
                continue
            redirects.append((f"{pkg}/{stub}", url, kind))

    if unresolved:
        for r in unresolved:
            print("UNRESOLVED", *r, file=sys.stderr)
        sys.exit("add rows to tools/overrides.csv for the pages above")

    with open(os.path.join(ROOT, "redirects.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["old_path", "new_url", "match_type"])
        w.writerows(redirects)
    with open(os.path.join(ROOT, "inventory", "unstubbed.csv"), "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["old_path", "reason"])
        w.writerows(sorted(unstubbed))
    print(f"{len(redirects)} redirects, {len(unstubbed)} unstubbed", file=sys.stderr)


if __name__ == "__main__":
    main()
