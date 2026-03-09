export type ValidationErrors = Record<string, string>

interface GraphQLErrorLike {
  message: string
  extensions?: Record<string, unknown>
}

function getGraphQLErrors(error: unknown): GraphQLErrorLike[] | null {
  if (typeof error !== 'object' || error === null) return null

  if ('errors' in error && Array.isArray((error as { errors: unknown }).errors)) {
    return (error as { errors: GraphQLErrorLike[] }).errors
  }

  if (
    'graphQLErrors' in error &&
    Array.isArray((error as { graphQLErrors: unknown }).graphQLErrors)
  ) {
    return (error as { graphQLErrors: GraphQLErrorLike[] }).graphQLErrors
  }

  return null
}

export function extractGraphQLErrors(error: unknown): {
  validationErrors: ValidationErrors
  hasValidationErrors: boolean
  unmappedErrors: string[]
} {
  const validationErrors: ValidationErrors = {}
  const unmappedErrors: string[] = []

  const gqlErrors = getGraphQLErrors(error)
  if (gqlErrors) {
    for (const gqlError of gqlErrors) {
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
