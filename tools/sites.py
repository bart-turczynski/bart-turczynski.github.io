"""Shared configuration: old GitHub Pages prefixes and their canonical GitLab Pages roots."""

OLD_ORIGIN = "https://bart-turczynski.github.io"

# GitHub Pages serves main:/docs, so everything published lives under this directory.
SITE_DIR = "docs"

# package prefix on the old user site -> canonical docs root (always ends in "/")
SITES = {
    "rurl": "https://bart-turczynski.gitlab.io/rurl/",
    "pagerankr": "https://bart-turczynski.gitlab.io/pagerankr/",
    "sitemapr": "https://bart-turczynski.gitlab.io/sitemapr/",
    "robotstxtr": "https://bart-turczynski.gitlab.io/robotstxtr/",
    "punycoder": "https://bart-turczynski.gitlab.io/punycoder/",
    "pslr": "https://bart-turczynski.gitlab.io/pslr/",
}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
DELAY = 0.3  # seconds between requests (polite, sequential)
