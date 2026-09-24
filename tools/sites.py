"""Shared configuration: old GitHub Pages prefixes and their canonical GitLab Pages roots."""

OLD_ORIGIN = "https://bart-turczynski.github.io"

# package prefix on the old user site -> canonical docs root (always ends in "/")
SITES = {
    "rurl": "https://bart-turczynski.gitlab.io/rurl/",
    "pagerankr": "https://pagerankr-63ad30.gitlab.io/",
    "sitemapr": "https://sitemapr-eca867.gitlab.io/",
    "robotstxtr": "https://robotstxtr-de6c15.gitlab.io/",
}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
DELAY = 0.3  # seconds between requests (polite, sequential)
