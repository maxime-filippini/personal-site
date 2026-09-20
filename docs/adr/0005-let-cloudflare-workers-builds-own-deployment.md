# Let Cloudflare Workers Builds own deployment

Cloudflare Workers Builds will build non-production branches into preview versions and deploy the production branch as the active Worker version. GitHub Actions may run repository checks but will not independently deploy the site. Keeping preview creation, image synchronization, version upload, and production promotion in Cloudflare avoids competing deployment state and removes the need for a custom publish webhook with production credentials.
