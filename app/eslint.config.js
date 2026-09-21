import js from '@eslint/js'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  {
    ignores: [
      '.output/**',
      '.tanstack/**',
      '.testing/**',
      '.wrangler/**',
      'dist/**',
      'node_modules/**',
      'playwright-report/**',
      'src/routeTree.gen.ts',
      'static/**',
      'test-results/**',
      'worker-configuration.d.ts',
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
)
