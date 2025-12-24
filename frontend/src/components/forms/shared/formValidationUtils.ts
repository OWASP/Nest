/**
 * Shared validation utilities for form components.
 */

export const validateRequired = (value: string, fieldName: string): string | undefined => {
  if (!value || (typeof value === 'string' && !value.trim())) {
    return `${fieldName} is required`
  }
  return undefined
}

export const validateName = (value: string, uniquenessError?: string): string | undefined => {
  const requiredError = validateRequired(value, 'Name')
  if (requiredError) return requiredError
  if (value.length > 200) return 'Name must be 200 characters or less'
  if (uniquenessError) return uniquenessError
  return undefined
}

export const validateDescription = (value: string): string | undefined => {
  return validateRequired(value, 'Description')
}

export const validateStartDate = (value: string): string | undefined => {
  return validateRequired(value, 'Start date')
}

export const validateEndDate = (value: string, startDate?: string): string | undefined => {
  const requiredError = validateRequired(value, 'End date')
  if (requiredError) return requiredError
  if (startDate && new Date(value) <= new Date(startDate)) {
    return 'End date must be after start date'
  }
  return undefined
}
