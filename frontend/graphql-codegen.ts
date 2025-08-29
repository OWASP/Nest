import { CodegenConfig } from '@graphql-codegen/cli'

const PUBLIC_API_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000'

const createCodegenConfig = async (): Promise<CodegenConfig> => {
  const response = await fetch(`${PUBLIC_API_URL}/csrf/`, {
    credentials: 'include',
    method: 'GET',
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  }
  const data = await response.json()
  const csrfToken = data.csrftoken

  return {
    documents: ['src/**/*.{ts,tsx}'],
    generates: {
      './src/types/__generated__/graphql.ts': {
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
        plugins: ['typescript', 'typescript-operations'],
      },
    },
    // Don't exit with non-zero status when there are no documents
    ignoreNoDocuments: true,
    overwrite: true,
    schema: {
      [`${PUBLIC_API_URL}/graphql/`]: {
        headers: {
          Cookie: `csrftoken=${csrfToken}`,
          'x-csrftoken': `${csrfToken}`,
        },
      },
    },
  }
}
export default await createCodegenConfig()
