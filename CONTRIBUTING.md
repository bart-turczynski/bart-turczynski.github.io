# Contributing

Install dependencies:

```sh
pnpm install
```

Run verification:

```sh
pnpm check
```

See the project README for the language-specific source, behavior-specification,
and test layout. Durable project context lives in `ARCHITECTURE.md` (the map) and
`design/` (specs and decision records); `docs/` is the published site.

Keep local-only planning state in `_scratch/`. Do not commit `_scratch/`, `.fp/`, secrets, dependency folders, build outputs, or generated caches.
