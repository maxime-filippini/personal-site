# Isolate local, preview, and production storage

Local development will use emulated R2 state, preview Worker versions will use a preview media bucket, and the active production Worker will use a production media bucket. Preview automation and experimental Effect programs will not receive production write access. Matching object conventions and bindings across the environments preserve realistic testing while preventing drafts or failed experiments from mutating production media.
