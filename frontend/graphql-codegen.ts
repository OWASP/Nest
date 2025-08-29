import { CodegenConfig } from '@graphql-codegen/cli'

const PUBLIC_API_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000'
let csrfToken = null

const fetchCsrfTokenServer = async (): Promise<string> => {
  if (csrfToken != null) {
    return csrfToken
  }
  const response = await fetch(`${PUBLIC_API_URL}/csrf/`, {
    credentials: 'include',
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  }
  const data = await response.json()
  csrfToken = data.csrftoken

  return data.csrftoken
}

const config: CodegenConfig = {
  overwrite: true,
  schema: {
    [`${PUBLIC_API_URL}/graphql/`]: {
      headers: {
        Cookie: `csrftoken=${await fetchCsrfTokenServer()}`,
        'x-csrftoken': `${await fetchCsrfTokenServer()}`,
      },
    },
  },
  documents: ['src/**/*.{ts,tsx}'],
  // Don't exit with non-zero status when there are no documents
  ignoreNoDocuments: true,
  generates: {
    './src/types/__generated__/graphql.ts': {
      plugins: ['typescript', 'typescript-operations'],
      config: {
        avoidOptionals: {
          // Use `null` for nullable fields instead of optionals
          field: true,
          // Allow nullable input fields to remain unspecified
          inputValue: false,
        },
        // Use `unknown` instead of `any` for unconfigured scalars
        defaultScalarType: 'unknown',
        // Apollo Client always includes `__typename` fields
        nonOptionalTypename: true,
        // Apollo Client doesn't add the `__typename` field to root types so
        // don't generate a type for the `__typename` for root operation types.
        skipTypeNameForRoot: true,
      },
    },
  },
}

export default config
