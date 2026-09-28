# bart-turczynski.github.io

The GitHub user site, `https://bart-turczynski.github.io/`. It does two jobs:

- **The root page** lists the R packages that have a GitHub repository, with
  links to their source on GitHub and their documentation on GitLab Pages. It
  is hand-written: `docs/index.html`.
- **Redirects** for the old GitHub Pages documentation of six R packages. Their
  documentation moved to GitLab Pages; every old URL under
  `https://bart-turczynski.github.io/<pkg>/...` goes to the equivalent page on
  the new host. Old links land on the matching page, not on a site home.

| Old prefix | Canonical docs |
|---|---|
| `/rurl/` | https://bart-turczynski.gitlab.io/rurl/ |
| `/pagerankr/` | https://bart-turczynski.gitlab.io/pagerankr/ |
| `/sitemapr/` | https://bart-turczynski.gitlab.io/sitemapr/ |
| `/robotstxtr/` | https://bart-turczynski.gitlab.io/robotstxtr/ |
| `/punycoder/` | https://bart-turczynski.gitlab.io/punycoder/ |
| `/pslr/` | https://bart-turczynski.gitlab.io/pslr/ |

Every package lives at the `bart-turczynski.gitlab.io/<pkg>/` namespace path
(SEOR-hcmtspmv, SEOR-vujgdjfv).

The GitLab user site, `https://bart-turczynski.gitlab.io/`, is a separate
project with its own package list and GitLab links. The two pages look alike
but are not mirrors: each links its own forge.

## How it is published

The source of truth is the GitLab repository. It is push-mirrored to the GitHub
user-site repository `bart-turczynski/bart-turczynski.github.io`, and GitHub
Pages serves that repository's **`docs/` folder** on `main`. Only `docs/` is
public; the rest of the repository (agent files, CI, tooling) is not served.
Never push to the GitHub copy directly.

**Per-project GitHub Pages must stay OFF** for every package listed above. A
GitHub repository with Pages enabled is served at
`bart-turczynski.github.io/<repo>/` and takes precedence over the same path in
this user site, so an enabled project site would hide these redirects.

## How the redirects work

- **One stub per old page.** Each old page (from `redirects.csv`) has a static
  HTML file at its old path under `docs/`, for example `docs/rurl/reference/get_host.html`, with a
  `<meta http-equiv="refresh">`, a `<link rel="canonical">`, a script doing
  `location.replace(target + location.hash)` so `#anchors` survive, and a
  visible link. Stubs are not `noindex`, so search engines can follow the
  canonical. A directory URL such as `/rurl/reference/` is served by its
  `index.html` stub.
- **`404.html`** handles any path without a stub, such as assets, `llms.txt`,
  `search.json` or pages added later. It sends `/<pkg>/<rest>` to
  `<new root><rest>` (keeping the query and fragment), so the fallback is still
  the same page, not the home page. Unknown prefixes show the package list.
- **`.nojekyll`** turns off Jekyll processing.

## Files

- `inventory/<pkg>.txt`: raw inventory of old URLs (path, old HTTP status,
  source: `sitemap`, `crawl`, `probe`, `new-sitemap`). punycoder and pslr were
  added after their old sites were gone, so their paths come from the new
  site's `sitemap.xml` (`new-sitemap`), and their files are hand-written, not
  crawled. `inventory/unstubbed.csv` lists the entries that get no stub and why: non-HTML files (handled by `404.html`),
  links that were already broken on the old site, and junk links.
- `redirects.csv`: `old_path,new_url,match_type`. `match_type` is `same`
  (the same path on the new host), `renamed` (an equivalent page under another
  name) or `section-fallback` (no successor exists, so the closest section is
  used, never the home page).
- `tools/overrides.csv`: the hand-picked `renamed` and `section-fallback`
  targets. Every one is listed there with a reason.
- `tools/`: Python 3 scripts, standard library only. They write the stubs,
  `404.html` and `.nojekyll` into `docs/`; they never touch `docs/index.html`.
- `src/`, `features/`: TypeScript checks of the root page (Cucumber).

## Regenerating

```sh
python3 tools/crawl_inventory.py   # re-crawl the old sites (only while they are still live; never for punycoder/pslr)
python3 tools/build_map.py         # inventory -> redirects.csv (verifies every target returns 200)
python3 tools/generate.py          # redirects.csv -> docs/: stubs, 404.html, .nojekyll
python3 tools/check.py             # self-check; --offline skips the HTTP checks
```

`build_map.py` fails when an old page has no same-path target and no override,
so a page can't silently fall back to a home page. `check.py` confirms that each
stub exists, that its refresh, canonical, script and link targets agree with
`redirects.csv` and with the generator's output, that every inventoried page is
covered, and that every target returns HTTP 200.

## Setup and verification

```sh
pnpm install
pre-commit install && pre-commit install --hook-type pre-push
pnpm check    # typecheck, root-page features, offline redirect self-check
```

`pnpm check` is the pre-push gate and the CI `verify` job.
