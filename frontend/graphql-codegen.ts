import { CodegenConfig } from '@graphql-codegen/cli'

const PUBLIC_API_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000'

let response: Response

try {
  response = await fetch(`${PUBLIC_API_URL}/csrf/`, {
    method: 'GET',
  })
} catch {
  /* eslint-disable no-console */
  console.log('Failed to fetch CSRF token: make sure the backend is running.')
  process.exit(1)
}

if (!response.ok) {
  console.log(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  process.exit(1)
}
const csrfToken = (await response.json()).csrftoken

const sharedOperationConfig = {
  config: {
    avoidOptionals: {
      // Use `null` for nullable fields instead of optionals
      field: true,
      // Allow nullable input fields to remain unspecified
      inputValue: false,
    },
    defaultScalarType: 'any',
    // Apollo Client always includes `__typename` fields
    nonOptionalTypename: true,
    // Apollo Client doesn't add the `__typename` field to root types so
    // don't generate a type for the `__typename` for root operation types.
    skipTypeNameForRoot: true,
  },
  plugins: ['typescript-operations', 'typed-document-node'],
  preset: 'near-operation-file',
  presetConfig: {
    baseTypesPath: './types/__generated__/graphql.ts',
  },
}

const config: CodegenConfig = {
  generates: {
    './src/': {
      ...sharedOperationConfig,
      documents: ['src/**/*.{ts,tsx}', '!src/types/__generated__/**', '!src/server/**'],
      presetConfig: {
        ...sharedOperationConfig.presetConfig,
        folder: '../types/__generated__',
      },
    },
    './src/server/': {
      ...sharedOperationConfig,
      documents: ['src/server/**/*.ts'],
      presetConfig: {
        ...sharedOperationConfig.presetConfig,
        // Resolved from baseOutputDir ./src/server/, so this points to src/types/__generated__/graphql.ts
        baseTypesPath: '../types/__generated__/graphql.ts',
        folder: '../../types/__generated__',
      },
    },
    './src/types/__generated__/graphql.ts': {
      config: {
        scalars: {
          // eslint-disable-next-line @typescript-eslint/naming-convention
          Date: 'string | number',
          // eslint-disable-next-line @typescript-eslint/naming-convention
          DateTime: 'string | number',
          JSON: 'Record<string, unknown>',
        },
      },
      plugins: ['typescript'],
    },
  },
  // Don't exit with non-zero status when there are no documents
  ignoreNoDocuments: true,
  overwrite: true,
  schema: {
    [`${PUBLIC_API_URL}/graphql/`]: {
      headers: {
        Cookie: `csrftoken=${csrfToken}`,
        'X-CSRFToken': csrfToken,
      },
    },
  },
}

export default config
