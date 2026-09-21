# Keep posts with the site

Post source and its assets will live in the site repository rather than a separate content repository. MDX posts may depend on site-owned React components, so keeping both together gives each commit a compatible, previewable version and avoids coordinating builds and credentials across repositories. Drafts will be reviewed through Cloudflare Worker preview deployments before publication.
