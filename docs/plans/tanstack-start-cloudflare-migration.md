# TanStack Start and Cloudflare migration

## Outcome

Replace the FastAPI site with a TanStack Start application on Cloudflare Workers while preserving the existing design, content, and reachable URLs. The replacement makes MDX the native post format, supports reusable React components inside posts, provides protected draft previews, and gives selected future pages access to independently produced runtime data.

The first production release is a parity migration. New pages such as `/now` and `/uses`, a redesign, search, comments, and browser-based editing follow after cutover.

## Target architecture

- TanStack Start owns routing, prerendering, request rendering, and hydration.
- Cloudflare Workers serves the application and handles the small set of routes that require runtime execution.
- Cloudflare static assets serves prerendered HTML and fingerprinted client assets.
- R2 stores content-addressed post images and, later, independently produced runtime data.
- Cloudflare Images transforms R2 image originals into a small set of responsive representations.
- Cloudflare Workers Builds creates protected previews for trusted non-production branches and deploys the production branch.
- Cloudflare Access restricts preview URLs to the author's identity using email one-time PIN authentication.
- Effect models validation, content processing, R2 services, typed failures, retries, and other effectful boundaries. React receives ordinary values.

## Proposed source layout

```text
content/
  posts/
    <post-directory>/
      index.mdx
      components/
      data/
      images/
docs/
  adr/
  plans/
  runbooks/
public/
scripts/
  cloudflare-bootstrap.ts
src/
  components/
    mdx/
  content/
  routes/
  services/
```

Each post owns its specialized components, data, and original images. Stable primitives such as `Note`, `Figure`, `PostImage`, and `CodeGroup` live in the shared MDX component directory. A specialized component moves into the shared set only after a second real use demonstrates the abstraction.

## Post model

Post metadata is validated during development and CI. The initial schema is intentionally small:

```yaml
title: Care for some CAViaR?
description: An introduction to …
slug: care-for-some-caviar
status: ready
publishedAt: 2026-09-17
updatedAt: 2026-09-19
```

- `slug` is explicit and stable after publication.
- A changed published slug must retain its previous value as a permanent redirect.
- `status` is `draft` or `ready`.
- `published` is an observed deployment outcome, not a frontmatter state.
- Drafts may omit `publishedAt`; ready posts may not.
- Duplicate slugs, invalid dates, illegal state combinations, broken imports, and missing assets fail validation.
- Additional metadata is introduced only for a concrete feature.

## Authoring workflow

```text
pnpm post:new <slug>
pnpm dev
pnpm content:check
pnpm post:ready <slug>
```

- `post:new` creates a co-located post directory and metadata template.
- The local dev server displays drafts with hot reload and local emulated bindings.
- `content:check` validates all content and referenced resources.
- `post:ready` validates one post, changes its state to ready, and supplies a publication date when absent.
- Authoring commands change only local files. Git operations and Cloudflare deployment remain explicit.
- A pushed trusted branch receives an Access-protected preview URL.
- Merging a ready post into the production branch triggers publication.
- Publication succeeds only after the active deployment serves the expected Git revision from the canonical URL.

## Rendering contract

Prerender at deployment time:

- `/`
- `/contact`
- `/cv`
- `/posts`
- every ready public post
- draft posts in preview builds
- RSS, sitemap, and the static error page

Render in the Worker only when a route depends on data produced independently of site publication. Interactive MDX elements may hydrate in the browser without making their containing route request-rendered. Every post remains useful and readable without JavaScript.

TanStack Start's client runtime is accepted as part of the learning objective. Post-specific code must remain route-scoped, and heavy components should use deferred hydration only after measurement justifies it.

## Image lifecycle

1. The original image is committed beside its post.
2. Validation checks the reference, required alternative text, and supported input format.
3. Preview or production automation hashes the original and checks its target R2 bucket.
4. A missing object is uploaded before the referencing Worker version is deployed.
5. `PostImage` emits responsive URLs for a small, named set of representations.
6. The Worker image route reads original bytes from R2 and transforms them through the Images binding.
7. Content-addressed URLs receive long-lived immutable caching.

Local development uses emulated R2 state. Preview and production use separate buckets and credentials. Preview automation cannot write production objects. The legacy R2 bucket remains passive after cutover and is not a dependency of the new application.

## Effect boundary

Use Effect for:

- metadata and runtime-document schemas;
- filesystem-based content discovery;
- post and link validation;
- image hashing and upload orchestration;
- R2 services and test layers;
- typed expected failures;
- retries, timeouts, bounded concurrency, configuration, and structured logging.

Run Effect programs at build-command, server-function, and route-loader boundaries. Do not introduce Effect into ordinary React rendering, local component state, or pure transformations.

## Deployment and security

- The repository is public but author-operated.
- Credentialed preview builds run only for trusted branches in the repository, not fork-originated pull requests.
- Preview automation has preview-only storage access.
- Production credentials are confined to the production-branch deployment.
- Workers Builds is the deployment authority; GitHub Actions may run checks but does not deploy.
- Preview URLs are protected by a default-deny Access policy allowing the author's exact email identity.
- Preview deployments send `X-Robots-Tag: noindex`.
- Production uses the custom domain and contains no draft routes or metadata.

## Cache and URL behavior

- Canonical URLs omit trailing slashes except `/`.
- Existing trailing-slash URLs permanently redirect to the canonical form.
- Prerendered HTML uses revalidation and ETags so a fresh navigation cannot retain stale content.
- Fingerprinted JavaScript and CSS use long-lived immutable caching.
- R2 media URLs are content-addressed and immutable.
- No service worker or publication-time global cache purge is introduced.
- Each build exposes its Git revision for smoke-test verification.

## Verification contract

Merge-blocking checks:

- formatting, linting, and TypeScript type checking;
- Vitest coverage for metadata rules, redirects, and Effect services with test layers;
- compilation of every MDX post;
- build-time proof that production contains no drafts;
- build-time proof that previews include drafts;
- validation of links, asset references, sitemap, RSS, canonical metadata, titles, and descriptions;
- Playwright checks of primary routes at desktop and phone widths;
- verification that substantive page content exists before hydration;
- image-route response and cache-header checks;
- existing URL and redirect checks.

Cutover-only checks:

- visual comparison of each existing page and all seven published posts;
- authorized and unauthorized Access login tests;
- production-domain smoke tests confirming the expected Git revision;
- manual review of mathematics, tables, code highlighting, images, notes, and document hierarchy.

## Infrastructure setup

`docs/runbooks/cloudflare-bootstrap.md` is the source of truth for prerequisites, permissions, resource names, dashboard steps, verification, troubleshooting, and explicit removal procedures.

An optional `scripts/cloudflare-bootstrap.ts` helper runs with Node through `tsx`:

```text
pnpm infra:check
pnpm infra:create
pnpm infra:verify
```

The helper is idempotent where practical, uses Wrangler rather than reimplementing its API calls, never embeds or prints secrets, and never deletes resources. Full Terraform or Pulumi management is deferred.

## Migration phases

### 1. Establish the toolchain

- Standardize on pnpm, a pinned Node version, TypeScript, and `tsx` for scripts.
- Scaffold TanStack Start with the Cloudflare Vite plugin and checked-in Wrangler configuration.
- Add formatting, linting, type checking, Vitest, and Playwright.
- Add local, preview, and production binding definitions.

### 2. Build the content system

- Define the Effect schemas and post lifecycle.
- Build content discovery, validation, and prerender path generation.
- Add the authoring commands.
- Add the first shared MDX primitives.

### 3. Recreate the public site

- Implement the existing routes and layout with visual parity.
- Preserve substantive content and metadata.
- Normalize canonical URLs and add permanent redirects.
- Generate RSS, sitemap, canonical metadata, and error pages.

### 4. Migrate posts

- Convert each existing Markdown post to reviewed MDX.
- Replace renderer-specific syntax with explicit components.
- Verify mathematics, code, tables, notes, and images.
- Add one genuinely interactive, static-by-default component to prove the model.

### 5. Add the media pipeline

- Create the preview and production buckets.
- Implement content-addressed upload orchestration with Effect.
- Implement `PostImage` and the Worker Images route.
- Verify cache behavior and environment isolation.

### 6. Configure delivery

- Connect the repository to Workers Builds.
- Enable trusted non-production branch previews.
- Protect preview URLs with Access.
- Configure production deployment, headers, redirects, and revision smoke tests.

### 7. Cut over

- Complete the preview and production-Worker checklists.
- Attach the custom domain to the verified Worker.
- Verify all canonical URLs and the deployed Git revision.
- Decommission the FastAPI service immediately.
- Retain the legacy R2 bucket passively.

## Deferred work

- `/now`, `/uses`, and other new pages;
- a general runtime-content system beyond an interface and focused integration test;
- visual redesign;
- CMS or browser editing;
- search, comments, accounts, or analytics redesign;
- full infrastructure as code;
- broad shared-component or Effect abstraction layers.

## Decision record

The architectural rationale is captured in [the ADR directory](../adr/), and the project language is defined in [the root context](../../CONTEXT.md).
