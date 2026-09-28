# bart-turczynski.github.io architecture

The living map of how this project is put together: directories, responsibilities,
seams, and invariants. Unlike a spec, this file must be true *right now* — it
describes the current structure, not a plan or a history.

Keep it coarse. Name directories and what they own; do not cite line numbers or
function signatures, which rot on the first refactor. Update it when the
structure changes, not when code changes.

For *why* a load-bearing choice was made, see the Architecture Decision Records
in [`design/adr/`](design/adr/). For *what* was built and to which requirements,
see [`design/specs/`](design/specs/).

## Overview

A static GitHub Pages user site. GitHub Pages serves `docs/` on `main` as is;
there is no build step. `docs/index.html` is a hand-written package list;
everything else in `docs/` is generated redirect stubs for the old per-package
documentation sites.

## Layout

<!--
Name every top-level source directory. `scripts/check-design.py` fails the push
if one is missing here — that check is the only thing standing between this file
and quiet rot.
-->

- `docs/` — the published site, served verbatim. `index.html` is hand-written;
  the `<pkg>/` stub trees, `404.html` and `.nojekyll` come from `tools/generate.py`.
- `tools/` — Python (stdlib only): crawl the old sites, build `redirects.csv`,
  generate the stubs, self-check them.
- `inventory/`, `redirects.csv` — the recorded old URLs and their targets.
- `src/` — TypeScript helpers that read the published root page.
- `features/` — Cucumber specs for the root page.

## Invariants

- Only `docs/` is published. Nothing outside it reaches the site.
- The root page links GitHub for source, never a GitLab repository.
  Documentation links go to GitLab Pages, the only place the docs exist.
- Generated files in `docs/` match `tools/generate.py` output byte for byte
  (`tools/check.py`).
