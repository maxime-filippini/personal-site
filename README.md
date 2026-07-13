# My personal site

This repository contains the server that powers [my personal website](https://maximefilippini.me).

It is a simple FastAPI server that serves HTML and converts markdown documents to HTML documents.

## Content repository

The nested `content/` directory is a separate Git repository and is
the local source of truth for blog posts and their assets. It deliberately
preserves the object layout used in production R2:

```text
content/
  posts/<slug>.md
  assets/<asset-path>
```

In development the server reads from `content/` by default. Set
`BLOG_CONTENT_DIR` to preview a different content checkout. Production continues
to read the same `posts/` and `assets/` layout from R2.
