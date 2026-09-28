import { readFileSync } from "node:fs";

/** One package entry on the root page. */
export interface PackageEntry {
  name: string;
  docs: string;
  source: string;
}

// Matches a list item as written in docs/index.html:
// <li><a href="DOCS">NAME</a>: description (<a href="SOURCE">source</a>)</li>
const ENTRY = /<li><a href="([^"]+)">([^<]+)<\/a>:[^<]*\(<a href="([^"]+)">source<\/a>\)<\/li>/g;
const HREF = /href="([^"]+)"/g;

export function readPage(path: string): string {
  return readFileSync(path, "utf8");
}

export function packageEntries(html: string): PackageEntry[] {
  return [...html.matchAll(ENTRY)].map(([, docs = "", name = "", source = ""]) => ({ name, docs, source }));
}

export function hrefs(html: string): string[] {
  return [...html.matchAll(HREF)].map(([, href = ""]) => href);
}
