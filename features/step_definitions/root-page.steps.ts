import assert from "node:assert/strict";
import { Given, Then, type DataTable } from "@cucumber/cucumber";
import { hrefs, packageEntries, readPage } from "../../src/page.js";
import type { PageWorld } from "../support/world.js";

Given("the published root page", function (this: PageWorld) {
  this.html = readPage("docs/index.html");
});

Then("it lists exactly these packages:", function (this: PageWorld, table: DataTable) {
  const expected = table.raw().map(([name = ""]) => name);
  assert.deepEqual(
    packageEntries(this.html).map((entry) => entry.name),
    expected,
  );
});

Then("each package links its source at {string}", function (this: PageWorld, pattern: string) {
  for (const entry of packageEntries(this.html)) {
    assert.equal(entry.source, pattern.replace("{name}", entry.name));
  }
});

Then("each package links its documentation at {string}", function (this: PageWorld, pattern: string) {
  for (const entry of packageEntries(this.html)) {
    assert.equal(entry.docs, pattern.replace("{name}", entry.name));
  }
});

Then("no link starts with {string}", function (this: PageWorld, prefix: string) {
  assert.deepEqual(
    hrefs(this.html).filter((href) => href.startsWith(prefix)),
    [],
  );
});
