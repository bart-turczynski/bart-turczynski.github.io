#!/usr/bin/env python3
"""Generate the static redirect site from redirects.csv (stdlib only).

Writes, relative to the published site directory (docs/):
  <old_path>        one stub per redirects.csv row (meta refresh + canonical + JS
                    location.replace that keeps the #fragment + visible link)
  404.html          maps any other /<pkg>/<rest> to <new root><rest> via JS
  .nojekyll

docs/index.html is hand-written and not touched here.

Stale stubs under a package prefix (files no longer in redirects.csv) are removed.

Usage: python3 tools/generate.py
"""
import csv
import json
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
from sites import SITE_DIR, SITES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, SITE_DIR)

STUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved: {title}</title>
<meta http-equiv="refresh" content="0; url={href}">
<link rel="canonical" href="{href}">
<script>location.replace({js} + location.hash);</script>
</head>
<body>
<p>This page has moved to <a href="{href}">{text}</a>.</p>
</body>
</html>
"""

NOT_FOUND = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page moved</title>
<script>
(function () {{
  var sites = {sites};
  var m = location.pathname.match(/^\\/([^\\/]+)(\\/.*)?$/);
  var root = m && Object.prototype.hasOwnProperty.call(sites, m[1]) ? sites[m[1]] : null;
  if (!root) return;
  var target = root + (m[2] || "/").replace(/^\\//, "") + location.search + location.hash;
  location.replace(target);
  document.addEventListener("DOMContentLoaded", function () {{
    var a = document.getElementById("moved");
    a.href = target;
    a.textContent = target;
    document.getElementById("hint").hidden = false;
  }});
}})();
</script>
<style>
:root {{ color-scheme: light dark; }}
body {{ font: 16px/1.5 system-ui, sans-serif; max-width: 40rem; margin: 3rem auto; padding: 0 16px; }}
</style>
</head>
<body>
<h1>Page moved</h1>
<p id="hint" hidden>This page has moved to <a id="moved" href="/">its new address</a>.</p>
<p>The package documentation now lives on GitLab Pages:</p>
<ul>
{items}
</ul>
</body>
</html>
"""

def items():
    return "\n".join(f'<li><a href="{escape(u)}">{escape(p)}</a></li>' for p, u in SITES.items())


def stub_html(old_path, url):
    return STUB.format(title=escape(old_path), href=escape(url, quote=True),
                       text=escape(url), js=json.dumps(url).replace("</", "<\\/"))


def write(rel, text):
    path = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def main():
    with open(os.path.join(ROOT, "redirects.csv")) as fh:
        rows = list(csv.DictReader(fh))
    wanted = set()
    for r in rows:
        old = r["old_path"]
        if old.split("/", 1)[0] not in SITES or ".." in old.split("/"):
            sys.exit(f"bad old_path {old!r}")
        write(old, stub_html(old, r["new_url"]))
        wanted.add(old)
    for pkg in SITES:  # drop stubs whose rows were removed
        for d, _, files in os.walk(os.path.join(SITE, pkg)):
            for f in files:
                rel = os.path.relpath(os.path.join(d, f), SITE)
                if rel not in wanted:
                    os.remove(os.path.join(d, f))
    write("404.html", NOT_FOUND.format(sites=json.dumps(SITES, indent=2), items=items()))
    write(".nojekyll", "")
    print(f"{len(rows)} stubs + 404.html + .nojekyll", file=sys.stderr)


if __name__ == "__main__":
    main()
