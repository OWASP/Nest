export type FieldErrors = Record<string, string>

interface GraphQLErrorLike {
  message: string
  extensions?: Record<string, unknown>
}

interface ApolloErrorLike {
  graphQLErrors: GraphQLErrorLike[]
}

function isApolloErrorLike(error: unknown): error is ApolloErrorLike {
  return (
    typeof error === 'object' &&
    error !== null &&
    'graphQLErrors' in error &&
    Array.isArray((error as ApolloErrorLike).graphQLErrors)
  )
}

export function extractFieldErrors(error: unknown): {
  fieldErrors: FieldErrors
  hasFieldErrors: boolean
  unmappedErrors: string[]
} {
  const fieldErrors: FieldErrors = {}
  const unmappedErrors: string[] = []

  if (isApolloErrorLike(error)) {
    for (const gqlError of error.graphQLErrors) {
      const extensions = gqlError.extensions
      if (typeof extensions?.field === 'string') {
        fieldErrors[extensions.field] = gqlError.message
      } else {
        unmappedErrors.push(gqlError.message)
      }
    }
  } else if (error instanceof Error && error.message) {
    unmappedErrors.push(error.message)
  }

  const hasFieldErrors = Object.keys(fieldErrors).length > 0
  return { fieldErrors, hasFieldErrors, unmappedErrors }
}
