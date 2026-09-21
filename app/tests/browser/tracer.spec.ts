import { expect, test } from '@playwright/test'

test('serves the prerendered migration tracer', async ({ page }) => {
  const response = await page.goto('/')

  expect(response?.ok()).toBe(true)
  await expect(page.getByTestId('migration-tracer')).toContainText(
    'TanStack Start is running on Cloudflare Workers.',
  )
})
