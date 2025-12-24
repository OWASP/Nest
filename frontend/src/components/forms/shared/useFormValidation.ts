import { useMemo } from 'react'

type ValidationRule = {
  field: string
  shouldValidate: boolean
  validator: () => string | undefined
}

/**
 * Custom hook for form validation that computes errors based on validation rules.
 *
 * @param validations - Array of validation rules to apply
 * @param dependencies - Dependencies array for useMemo (typically formData, touched, and other relevant state)
 * @returns Record of field names to error messages (undefined if no error)
 */
export const useFormValidation = (
  validations: ValidationRule[],
  dependencies: unknown[]
): Record<string, string | undefined> => {
  return useMemo(() => {
    const errs: Record<string, string | undefined> = {}

    validations.forEach(({ field, shouldValidate, validator }) => {
      if (shouldValidate) {
        errs[field] = validator()
      }
    })

    return errs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies)
}
