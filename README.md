# My personal site

This repository contains the server that powers [my personal website](https://maximefilippini.me).

It is a simple FastAPI server that serves HTML and converts markdown documents to HTML documents.

## Content publishing

The content publisher refreshes changed posts by calling the protected update
endpoints with `Authorization: Bearer <token>`. Set `PUBLISH_TOKEN` in the
server environment to a long, randomly generated value. Store that same value
as the `SITE_PUBLISH_TOKEN` GitHub Actions secret in the separate content
repository; it must never be committed to either repository.
