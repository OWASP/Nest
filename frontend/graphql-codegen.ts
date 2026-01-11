import { CodegenConfig } from '@graphql-codegen/cli'

const PUBLIC_API_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000'
type CsrfResponse = {
  csrftoken?: string
}


export default async function graphqlCodegenConfig(): Promise<CodegenConfig> {
  let response: Response

  try {
    response = await fetch(`${PUBLIC_API_URL}/csrf/`, {
      method: 'GET',
    })
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('Failed to fetch CSRF token: make sure the backend is running.', err)
    throw new Error('Failed to fetch CSRF token', { cause: err })
  }

  if (!response.ok) {
    throw new Error(`Failed to fetch CSRF token: ${response.status} ${response.statusText}`)
  }

  let body: unknown

  try {
    body = await response.json()
  } catch (err) {
    throw new Error(
      `Failed to parse CSRF token response: ${response.status} ${response.statusText}`,
      { cause: err }
    )
  }

  const data = body as CsrfResponse

  const csrfToken =
  typeof data.csrftoken === 'string' && data.csrftoken.trim() !== ''
    ? data.csrftoken
    : null


  if (!csrfToken) {
    throw new Error("Failed to fetch CSRF token: missing or invalid 'csrftoken' in response body")
  }

  return {
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
}
