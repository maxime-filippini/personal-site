# Revalidate HTML and immutably cache content-addressed assets

Prerendered HTML will use Cloudflare's revalidate-on-use static-asset behavior, while fingerprinted JavaScript, CSS, and content-addressed R2 images will use long-lived immutable browser caching. Each deployment will embed its Git revision, and publication succeeds only after the canonical post URL serves the expected revision. Because changed assets receive new URLs and Worker versions include their static assets, publication and rollback require no broad cache purge.
