import { createHash } from 'node:crypto'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { extname, join, relative, resolve } from 'node:path'

import { parse } from 'yaml'

type PostState = 'draft' | 'ready'

interface SourceProvenance {
  repository: string
  revision: string
  expected: {
    posts: number
    ready: number
    drafts: number
    assets: number
  }
}

interface PostMetadata {
  title: string
  posted_on: string
  last_update: string
  abstract: string
  draft: boolean
}

interface PostInventory {
  slug: string
  state: PostState
  source: string
  sha256: string
  metadata: PostMetadata
  assetReferences: string[]
  missingAssetReferences: string[]
}

export interface ContentInventory {
  schemaVersion: 1
  source: SourceProvenance
  totals: {
    posts: number
    ready: number
    drafts: number
    assets: number
    referencedAssets: number
    missingAssetReferences: number
  }
  posts: PostInventory[]
  assets: string[]
}

const FRONTMATTER = /^---\s*\r?\n([\s\S]*?)\r?\n---\s*(?:\r?\n|$)/
const ASSET_REFERENCE = /\/assets\/([^\s)"'>]+)/g
const REQUIRED_METADATA = [
  'title',
  'posted_on',
  'last_update',
  'abstract',
  'draft',
] as const

function listFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? listFiles(path) : [path]
  })
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function stringField(
  metadata: Record<string, unknown>,
  field: keyof Omit<PostMetadata, 'draft'>,
  source: string,
): string {
  const value = metadata[field]
  if (typeof value !== 'string') {
    throw new Error(`${source}: frontmatter field "${field}" must be a string`)
  }
  return value
}

function parseMetadata(markdown: string, source: string): PostMetadata {
  const match = markdown.match(FRONTMATTER)
  if (!match?.[1]) {
    throw new Error(`${source}: missing YAML frontmatter`)
  }

  const parsed: unknown = parse(match[1])
  if (!isRecord(parsed)) {
    throw new Error(`${source}: frontmatter must be a mapping`)
  }

  for (const field of REQUIRED_METADATA) {
    if (!(field in parsed)) {
      throw new Error(`${source}: missing frontmatter field "${field}"`)
    }
  }

  if (typeof parsed.draft !== 'boolean') {
    throw new Error(`${source}: frontmatter field "draft" must be a boolean`)
  }

  return {
    title: stringField(parsed, 'title', source),
    posted_on: stringField(parsed, 'posted_on', source),
    last_update: stringField(parsed, 'last_update', source),
    abstract: stringField(parsed, 'abstract', source),
    draft: parsed.draft,
  }
}

function findAssetReferences(markdown: string): string[] {
  return [
    ...new Set(
      [...markdown.matchAll(ASSET_REFERENCE)].flatMap((match) =>
        match[1] ? [match[1].split(/[?#]/, 1)[0]] : [],
      ),
    ),
  ].sort()
}

function readSource(contentDirectory: string): SourceProvenance {
  const sourcePath = join(contentDirectory, 'source.json')
  const parsed: unknown = JSON.parse(readFileSync(sourcePath, 'utf8'))
  if (!isRecord(parsed) || !isRecord(parsed.expected)) {
    throw new Error(`${sourcePath}: invalid source provenance`)
  }

  const { repository, revision, expected } = parsed
  if (
    typeof repository !== 'string' ||
    typeof revision !== 'string' ||
    typeof expected.posts !== 'number' ||
    typeof expected.ready !== 'number' ||
    typeof expected.drafts !== 'number' ||
    typeof expected.assets !== 'number'
  ) {
    throw new Error(`${sourcePath}: invalid source provenance fields`)
  }

  return {
    repository,
    revision,
    expected: {
      posts: expected.posts,
      ready: expected.ready,
      drafts: expected.drafts,
      assets: expected.assets,
    },
  }
}

export function buildContentInventory(rootDirectory: string): ContentInventory {
  const root = resolve(rootDirectory)
  const contentDirectory = join(root, 'content')
  const postsDirectory = join(contentDirectory, 'posts')
  const assetsDirectory = join(contentDirectory, 'assets')
  const source = readSource(contentDirectory)

  const assets = listFiles(assetsDirectory)
    .map((file) => relative(assetsDirectory, file).replaceAll('\\', '/'))
    .sort()

  const posts = listFiles(postsDirectory)
    .filter((file) => extname(file) === '.md')
    .sort()
    .map((file): PostInventory => {
      const markdown = readFileSync(file, 'utf8')
      const sourcePath = relative(root, file).replaceAll('\\', '/')
      const assetReferences = findAssetReferences(markdown)
      const metadata = parseMetadata(markdown, sourcePath)

      return {
        slug: file.slice(postsDirectory.length + 1, -extname(file).length),
        state: metadata.draft ? 'draft' : 'ready',
        source: sourcePath,
        sha256: createHash('sha256').update(markdown).digest('hex'),
        metadata,
        assetReferences,
        missingAssetReferences: assetReferences.filter(
          (asset) => !existsSync(join(assetsDirectory, asset)),
        ),
      }
    })

  const referencedAssets = new Set(
    posts.flatMap((post) => post.assetReferences),
  )

  return {
    schemaVersion: 1,
    source,
    totals: {
      posts: posts.length,
      ready: posts.filter((post) => post.state === 'ready').length,
      drafts: posts.filter((post) => post.state === 'draft').length,
      assets: assets.length,
      referencedAssets: referencedAssets.size,
      missingAssetReferences: posts.reduce(
        (count, post) => count + post.missingAssetReferences.length,
        0,
      ),
    },
    posts,
    assets,
  }
}

export function serializeInventory(inventory: ContentInventory): string {
  return `${JSON.stringify(inventory, null, 2)}\n`
}
