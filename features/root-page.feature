Feature: Root page
  The root page lists the R packages that have a GitHub repository. Source
  links stay on GitHub; documentation links go to GitLab Pages, the only place
  the documentation is published.

  Background:
    Given the published root page

  Scenario: Every listed package links its GitHub source and its documentation
    Then it lists exactly these packages:
      | pagerankr  |
      | pslr       |
      | punycoder  |
      | raddr      |
      | robotstxtr |
      | rurl       |
      | seor       |
      | sitemapr   |
    And each package links its source at "https://github.com/bart-turczynski/{name}"
    And each package links its documentation at "https://bart-turczynski.gitlab.io/{name}/"

  Scenario: The page links no GitLab repository
    Then no link starts with "https://gitlab.com/"
