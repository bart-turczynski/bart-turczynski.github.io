import { setWorldConstructor } from "@cucumber/cucumber";

export class PageWorld {
  html = "";
}

setWorldConstructor(PageWorld);
