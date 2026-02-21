import { extractFieldErrors } from 'utils/helpers/handleGraphQLError'

describe('extractFieldErrors', () => {
  describe('ApolloError-like errors with graphQLErrors', () => {
    it('extracts field errors from graphQLErrors with field extension', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'This module name already exists in this program.',
            extensions: { code: 'VALIDATION_ERROR', field: 'name' },
          },
        ],
      }

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(true)
      expect(result.fieldErrors).toEqual({
        name: 'This module name already exists in this program.',
      })
      expect(result.unmappedErrors).toEqual([])
    })

    it('extracts multiple field errors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Name is required.',
            extensions: { field: 'name' },
          },
          {
            message: 'Description is too short.',
            extensions: { field: 'description' },
          },
        ],
      }

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(true)
      expect(result.fieldErrors).toEqual({
        name: 'Name is required.',
        description: 'Description is too short.',
      })
      expect(result.unmappedErrors).toEqual([])
    })

    it('puts errors without field extension into unmappedErrors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Something went wrong.',
            extensions: { code: 'INTERNAL_ERROR' },
          },
        ],
      }

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
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

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Unauthorized.'])
    })

    it('separates field errors from unmapped errors', () => {
      const error = {
        graphQLErrors: [
          {
            message: 'Name already exists.',
            extensions: { field: 'name' },
          },
          {
            message: 'Internal server error.',
            extensions: { code: 'INTERNAL_ERROR' },
          },
        ],
      }

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(true)
      expect(result.fieldErrors).toEqual({ name: 'Name already exists.' })
      expect(result.unmappedErrors).toEqual(['Internal server error.'])
    })

    it('handles empty graphQLErrors array', () => {
      const error = { graphQLErrors: [] }

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })
  })

  describe('plain Error objects', () => {
    it('puts Error message into unmappedErrors', () => {
      const error = new Error('Network error')

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Network error'])
    })

    it('puts generic Error message into unmappedErrors', () => {
      const error = new Error('Something went wrong')

      const result = extractFieldErrors(error)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual(['Something went wrong'])
    })
  })

  describe('non-Error values', () => {
    it('returns empty results for string error', () => {
      const result = extractFieldErrors('string error')

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for null', () => {
      const result = extractFieldErrors(null)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for undefined', () => {
      const result = extractFieldErrors(undefined)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })

    it('returns empty results for number', () => {
      const result = extractFieldErrors(42)

      expect(result.hasFieldErrors).toBe(false)
      expect(result.fieldErrors).toEqual({})
      expect(result.unmappedErrors).toEqual([])
    })
  })
})
