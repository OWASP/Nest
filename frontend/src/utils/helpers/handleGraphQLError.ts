export type ValidationErrors = Record<string, string>

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

export function extractGraphQLErrors(error: unknown): {
  validationErrors: ValidationErrors
  hasValidationErrors: boolean
  unmappedErrors: string[]
} {
  const validationErrors: ValidationErrors = {}
  const unmappedErrors: string[] = []

  if (isApolloErrorLike(error)) {
    for (const gqlError of error.graphQLErrors) {
      // const extensions = gqlError.extensions
      const extensions = gqlError.extensions as { code?: string; field?: unknown } | undefined
      if (extensions?.code === 'VALIDATION_ERROR' && typeof extensions.field === 'string') {
        validationErrors[extensions.field] = gqlError.message
      } else {
        unmappedErrors.push(gqlError.message)
      }
    }
  } else if (error instanceof Error && error.message) {
    unmappedErrors.push(error.message)
  }

  const hasValidationErrors = Object.keys(validationErrors).length > 0
  return { validationErrors, hasValidationErrors, unmappedErrors }
}
