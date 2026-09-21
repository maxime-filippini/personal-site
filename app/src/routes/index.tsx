import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: Home })

function Home() {
  return (
    <main data-testid="migration-tracer">
      <p className="eyebrow">Migration tracer</p>
      <h1>TanStack Start is running on Cloudflare Workers.</h1>
      <p>
        This prerendered route proves the new application can run beside the
        existing FastAPI site while the migration is in progress.
      </p>
    </main>
  )
}
