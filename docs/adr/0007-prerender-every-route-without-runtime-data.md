# Prerender every route without runtime data

Public pages and posts will be prerendered at deployment time unless a route has a concrete dependency on independently produced runtime data. Routes with such a dependency may render complete HTML in the Worker, while interactive MDX elements hydrate in the browser without forcing their containing page into request-time rendering. This keeps ordinary site delivery independent of Worker execution while preserving one TanStack Start application for static, server-rendered, and interactive experiences.
