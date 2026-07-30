import type { ValidationRule } from 'components/forms/shared/useFormValidation'

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

export const validateFileExtension = (
  file: File,
  allowedExtensions: string[]
): string | undefined => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!allowedExtensions.some((e) => e.toLowerCase() === ext)) {
    return `File extension .${ext} is not supported. Allowed: ${allowedExtensions.join(', ')}`
  }
  return undefined
}

export const validateFileSize = (file: File, maxSizeMb: number): string | undefined => {
  const size = file.size
  if (size > maxSizeMb * 1024 * 1024) {
    return `File size must be under ${maxSizeMb} MB.`
  }
  return undefined
}

type CommonFormData = {
  name: string
  description: string
  startedAt: string
  endedAt: string
}

type CommonTouched = {
  name?: boolean
  description?: boolean
  startedAt?: boolean
  endedAt?: boolean
}

export const getCommonValidationRules = (
  formData: CommonFormData,
  touched: CommonTouched,
  validateNameLocal: (value: string) => string | undefined,
  validateEndDateLocal: (value: string) => string | undefined
): ValidationRule[] => {
  return [
    {
      field: 'name',
      shouldValidate: touched.name ?? false,
      validator: () => validateNameLocal(formData.name),
    },
    {
      field: 'description',
      shouldValidate: touched.description ?? false,
      validator: () => validateDescription(formData.description),
    },
    {
      field: 'startedAt',
      shouldValidate: touched.startedAt ?? false,
      validator: () => validateStartDate(formData.startedAt),
    },
    {
      field: 'endedAt',
      shouldValidate:
        (touched.endedAt ?? false) || ((touched.startedAt ?? false) && !!formData.endedAt),
      validator: () => validateEndDateLocal(formData.endedAt),
    },
  ]
}
