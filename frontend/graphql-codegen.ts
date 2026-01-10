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
  throw new Error('Failed to fetch CSRF token')
}

if (!response.ok) {
  throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
}

const csrfToken = (await response.json()).csrftoken

const config: CodegenConfig = {
  documents: ['src/**/*.{ts,tsx}', '!src/types/__generated__/**'],
  generates: {
    './src/': {
      config: {
        avoidOptionals: {
          field: true,
          inputValue: false,
        },
        defaultScalarType: 'any',
        nonOptionalTypename: true,
        skipTypeNameForRoot: true,
      },
      plugins: ['typescript-operations', 'typed-document-node'],
      preset: 'near-operation-file',
      presetConfig: {
        baseTypesPath: './types/__generated__/graphql.ts',
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
