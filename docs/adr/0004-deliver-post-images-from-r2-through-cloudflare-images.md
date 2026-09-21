# Deliver post images from R2 through Cloudflare Images

Original post images will remain beside their posts in Git, then publication will upload content-addressed copies to R2 before deploying pages that reference them. A Worker image route backed by Cloudflare Images will create and cache a small set of responsive representations on demand instead of CI generating derivative files. This adds modest platform complexity in exchange for reproducible sources, immutable references, a simpler publication pipeline, and practical experience with R2 and Cloudflare bindings.
