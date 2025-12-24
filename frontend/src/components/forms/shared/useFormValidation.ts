import { useMemo } from 'react'

export type ValidationRule = {
  field: string
  shouldValidate: boolean
  validator: () => string | undefined
}

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
