import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'

describe('extractGraphQLErrors', () => {
  describe('ApolloError-like errors with graphQLErrors', () => {
    it('extracts validation errors when code is VALIDATION_ERROR and field is present', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'This module name already exists in this program.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(true)
      expect(result.validationErrors).toEqual({
        name: 'This module name already exists in this program.',
      })
      expect(result.unmappedErrors).toEqual([])
    })

    it('extracts multiple validation errors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Name is required.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
          {
            message: 'Description is too short.',
            extensions: { code: 'VALIDATION_ERROR', field: 'description' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(true)
      expect(result.validationErrors).toEqual({
        name: 'Name is required.',
        description: 'Description is too short.',
      })
      expect(result.unmappedErrors).toEqual([])
    })

    it('puts errors with non-validation code into unmappedErrors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Something went wrong.',
            extensions: { code: 'INTERNAL_ERROR' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Something went wrong.'])
    })

    it('puts errors without extensions into unmappedErrors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Unauthorized.',
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Unauthorized.'])
    })

    it('puts VALIDATION_ERROR without field into unmappedErrors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Validation failed.',
            extensions: { code: 'VALIDATION_ERROR' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Validation failed.'])
    })

    it('puts errors with field but without VALIDATION_ERROR code into unmappedErrors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Field-level error without code.',
            extensions: { field: 'name' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Field-level error without code.'])
    })

    it('separates validation errors from unmapped errors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Name already exists.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
          {
            message: 'Internal server error.',
            extensions: { code: 'INTERNAL_ERROR' },
          },
        ],
      }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(true)
      expect(result.validationErrors).toEqual({ name: 'Name already exists.' })
      expect(result.unmappedErrors).toEqual(['Internal server error.'])
    })

    it('handles empty graphQLErrors array', () => {
      const error = { graphQLErrors: [] }

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })
  })

  describe('plain Error objects', () => {
    it('puts Error message into unmappedErrors', () => {
      const error = new Error('Network error')

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Network error'])
    })

    it('puts generic Error message into unmappedErrors', () => {
      const error = new Error('Something went wrong')

      const result = extractGraphQLErrors(error)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Something went wrong'])
    })
  })

  describe('non-Error values', () => {
    it('returns empty results for string error', () => {
      const result = extractGraphQLErrors('string error')

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for null', () => {
      const result = extractGraphQLErrors(null)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for undefined', () => {
      const result = extractGraphQLErrors(undefined)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for number', () => {
      const result = extractGraphQLErrors(42)

      expect(result.hasValidationErrors).toBe(false)
      expect(result.validationErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })
  })
})
