# Make interactive posts static by default

Published posts and their interactive elements will be self-contained by default: their prose, inputs, and meaningful initial state are fixed by the deployed revision, while browser-side interaction may hydrate after rendering. Explicit components may use live Worker or R2 data when the subject requires it, but the post must retain a useful snapshot or explanation if that service is unavailable. This keeps old writing reproducible without preventing deliberate experiments with live Cloudflare services.
