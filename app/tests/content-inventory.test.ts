import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { expect, test } from 'vitest'

import { buildContentInventory } from '../src/content/inventory'

test('reports post states and missing asset references', () => {
  const root = mkdtempSync(join(tmpdir(), 'personal-site-content-'))
  const posts = join(root, 'content/posts')
  const assets = join(root, 'content/assets/images')
  mkdirSync(posts, { recursive: true })
  mkdirSync(assets, { recursive: true })
  writeFileSync(
    join(root, 'content/source.json'),
    JSON.stringify({
      repository: 'example/content',
      revision: 'abc123',
      expected: { posts: 1, ready: 1, drafts: 0, assets: 1 },
    }),
  )
  writeFileSync(join(assets, 'present.png'), 'image')
  writeFileSync(
    join(posts, 'hello.md'),
    `---
title: Hello
posted_on: "2026-09-20"
last_update: "2026-09-20"
draft: false
abstract: A post
---

![Present](/assets/images/present.png)
![Missing](/assets/images/missing.png)
`,
  )

  const inventory = buildContentInventory(root)

  expect(inventory.totals).toMatchObject({
    posts: 1,
    ready: 1,
    drafts: 0,
    assets: 1,
    referencedAssets: 2,
    missingAssetReferences: 1,
  })
  expect(inventory.posts[0]).toMatchObject({
    slug: 'hello',
    state: 'ready',
    missingAssetReferences: ['images/missing.png'],
  })
})

test('reports invalid frontmatter with its source path', () => {
  const root = mkdtempSync(join(tmpdir(), 'personal-site-content-'))
  const posts = join(root, 'content/posts')
  mkdirSync(posts, { recursive: true })
  mkdirSync(join(root, 'content/assets'), { recursive: true })
  writeFileSync(
    join(root, 'content/source.json'),
    JSON.stringify({
      repository: 'example/content',
      revision: 'abc123',
      expected: { posts: 1, ready: 1, drafts: 0, assets: 0 },
    }),
  )
  writeFileSync(
    join(posts, 'invalid.md'),
    `---
title: 42
posted_on: "2026-09-20"
last_update: "2026-09-20"
draft: false
abstract: A post
---
`,
  )

  expect(() => buildContentInventory(root)).toThrowError(
    /content\/posts\/invalid\.md: invalid frontmatter[\s\S]*frontmatter field "title" must be a string/,
  )
})

test('validates source provenance', () => {
  const root = mkdtempSync(join(tmpdir(), 'personal-site-content-'))
  mkdirSync(join(root, 'content/posts'), { recursive: true })
  mkdirSync(join(root, 'content/assets'), { recursive: true })
  writeFileSync(
    join(root, 'content/source.json'),
    JSON.stringify({
      repository: 'example/content',
      revision: 'abc123',
      expected: { posts: 'one', ready: 1, drafts: 0, assets: 0 },
    }),
  )

  expect(() => buildContentInventory(root)).toThrowError(
    /source\.json: invalid source provenance[\s\S]*expected\.posts must be a number/,
  )
})
