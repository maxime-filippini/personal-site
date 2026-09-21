import { createHash } from 'node:crypto'
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { extname, join, relative, resolve } from 'node:path'

import * as v from 'valibot'
import { parse } from 'yaml'

type PostState = 'draft' | 'ready'

const PostMetadataSchema = v.object(
  {
    title: v.string('frontmatter field "title" must be a string'),
    posted_on: v.string('frontmatter field "posted_on" must be a string'),
    last_update: v.string(
      'frontmatter field "last_update" must be a string',
    ),
    abstract: v.string('frontmatter field "abstract" must be a string'),
    draft: v.boolean('frontmatter field "draft" must be a boolean'),
  },
  'frontmatter must be a mapping',
)

const SourceProvenanceSchema = v.object(
  {
    repository: v.string('repository must be a string'),
    revision: v.string('revision must be a string'),
    expected: v.object({
      posts: v.number('expected.posts must be a number'),
      ready: v.number('expected.ready must be a number'),
      drafts: v.number('expected.drafts must be a number'),
      assets: v.number('expected.assets must be a number'),
    }),
  },
  'source provenance must be an object',
)

const SourceFileSchema = v.pipe(
  v.string(),
  v.parseJson(undefined, 'source provenance must contain valid JSON'),
  SourceProvenanceSchema,
)

type PostMetadata = v.InferOutput<typeof PostMetadataSchema>
type SourceProvenance = v.InferOutput<typeof SourceProvenanceSchema>

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

function listFiles(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name)
    return entry.isDirectory() ? listFiles(path) : [path]
  })
}

function parseMetadata(markdown: string, source: string): PostMetadata {
  const match = markdown.match(FRONTMATTER)
  if (!match?.[1]) {
    throw new Error(`${source}: missing YAML frontmatter`)
  }

  const result = v.safeParse(PostMetadataSchema, parse(match[1]))
  if (!result.success) {
    throw new Error(
      `${source}: invalid frontmatter\n${v.summarize(result.issues)}`,
    )
  }

  return result.output
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
  const result = v.safeParse(
    SourceFileSchema,
    readFileSync(sourcePath, 'utf8'),
  )
  if (!result.success) {
    throw new Error(
      `${sourcePath}: invalid source provenance\n${v.summarize(result.issues)}`,
    )
  }

  return result.output
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
