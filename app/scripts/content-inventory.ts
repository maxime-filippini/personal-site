import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

import {
  buildContentInventory,
  serializeInventory,
} from '../src/content/inventory'

const root = resolve(import.meta.dirname, '..')
const inventoryPath = resolve(root, 'content/inventory.json')
const inventory = buildContentInventory(root)
const serialized = serializeInventory(inventory)

if (process.argv.includes('--write')) {
  writeFileSync(inventoryPath, serialized)
  console.log(`Wrote ${inventoryPath}`)
} else if (process.argv.includes('--check')) {
  const expected = inventory.source.expected
  const errors: string[] = []

  for (const field of ['posts', 'ready', 'drafts', 'assets'] as const) {
    if (inventory.totals[field] !== expected[field]) {
      errors.push(
        `Expected ${String(expected[field])} ${field}, found ${String(inventory.totals[field])}`,
      )
    }
  }

  if (inventory.totals.missingAssetReferences !== 0) {
    errors.push(
      `Found ${String(inventory.totals.missingAssetReferences)} missing asset references`,
    )
  }

  if (readFileSync(inventoryPath, 'utf8') !== serialized) {
    errors.push('content/inventory.json is stale; run pnpm content:inventory:write')
  }

  if (errors.length > 0) {
    throw new Error(errors.join('\n'))
  }

  console.log(
    `Content inventory valid: ${String(inventory.totals.ready)} ready, ${String(inventory.totals.drafts)} drafts, ${String(inventory.totals.assets)} assets, no missing references.`,
  )
} else {
  process.stdout.write(serialized)
}
