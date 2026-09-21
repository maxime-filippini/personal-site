# Legacy FastAPI application

This directory contains the existing server, static assets, Docker setup, and
JavaScript tooling. It remains available during the TanStack Start migration.

Run commands from this directory. The original development command is:

```bash
bun run serve
```

The development configuration reads posts from `../app/content` by default.
Set `BLOG_CONTENT_DIR` explicitly to use another checkout. The existing
environment variables and production R2 configuration are still required.

## Content publishing

The separate legacy publisher refreshes changed posts by calling the protected
update endpoints with `Authorization: Bearer <token>`. Set `PUBLISH_TOKEN` in
the server environment to a long, randomly generated value. Store that same
value as the `SITE_PUBLISH_TOKEN` GitHub Actions secret in the separate content
repository; it must never be committed to either repository.
