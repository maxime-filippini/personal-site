# Treat content and preview branches as trusted code

MDX, post-specific React components, and repository build scripts are executable code, so credentialed preview builds will run only for trusted branches pushed within the author-operated repository. Fork-originated changes will not automatically receive Cloudflare credentials or deployments. Preview automation will have access only to preview resources, and production credentials will remain confined to production-branch deployment.
