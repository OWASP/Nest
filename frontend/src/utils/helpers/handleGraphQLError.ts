export type ValidationErrors = Record<string, string>

interface GraphQLErrorLike {
  message: string
  extensions?: Record<string, unknown>
}

function getGraphQLErrors(error: unknown): GraphQLErrorLike[] | null {
  if (typeof error !== 'object' || error === null) return null

  let candidates: unknown[] | null = null
  if ('errors' in error && Array.isArray((error as { errors: unknown }).errors)) {
    candidates = (error as { errors: unknown[] }).errors
  } else if (
    'graphQLErrors' in error &&
    Array.isArray((error as { graphQLErrors: unknown }).graphQLErrors)
  ) {
    candidates = (error as { graphQLErrors: unknown[] }).graphQLErrors
  }

  if (!candidates || candidates.length === 0) return null

  const gqlErrors = candidates.filter(
    (item): item is GraphQLErrorLike =>
      typeof item === 'object' &&
      item !== null &&
      typeof (item as GraphQLErrorLike).message === 'string'
  )

  return gqlErrors.length > 0 ? gqlErrors : null
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
