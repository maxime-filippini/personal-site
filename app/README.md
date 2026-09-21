# TanStack Start application

This is the replacement personal-site application. It targets Cloudflare
Workers and owns the versioned post corpus in `content/`.

The toolchain is pinned to Node 22.22.1 and pnpm 11.23.0. Run commands from
this directory:

```bash
pnpm install
pnpm dev
```

`pnpm build` prerenders the migration tracer at `/`, and `pnpm preview` serves
the production build through the Cloudflare Vite integration. Run all checks
with `pnpm check`. Before the first browser test on a new machine, install its
runtime with `pnpm exec playwright install --with-deps chromium`.

## Post source

Posts live in `content/posts`, with their original assets in `content/assets`.
They were imported unchanged from the revision recorded in
`content/source.json`.

Run `pnpm content:check` to verify the committed inventory, expected post
states, source hashes, and asset references. After an intentional content
change, regenerate `content/inventory.json` with
`pnpm content:inventory:write` and review the diff.
