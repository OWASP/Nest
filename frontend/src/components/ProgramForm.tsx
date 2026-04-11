'use client'

import type React from 'react'
import { useState } from 'react'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormDateInput } from 'components/forms/shared/FormDateInput'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import {
  getCommonValidationRules,
  validateDescription,
  validateEndDate,
  validateName,
  validateStartDate,
} from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'

interface ProgramFormProps {
  formData: {
    name: string
    description: string
    menteesLimit: number
    startedAt: string
    endedAt: string
    tags: string
    domains: string
    adminLogins?: string
    status?: string
  }
  setFormData: React.Dispatch<
    React.SetStateAction<{
      name: string
      description: string
      menteesLimit: number
      startedAt: string
      endedAt: string
      tags: string
      domains: string
      adminLogins?: string
      status?: string
    }>
  >
  onSubmit: (e: React.FormEvent) => Promise<void>
  loading: boolean
  title: string
  submitText?: string
  isEdit?: boolean
}

const ProgramForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
}: ProgramFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})

  const handleInputChange = (name: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (backendErrors[name]) {
      setBackendErrors((prev) => {
        const next = { ...prev }
        delete next[name]
        return next
      })
    }
  }

  const validateNameLocal = (value: string): string | undefined => {
    return validateName(value, backendErrors.name)
  }

  const validateEndDateLocal = (value: string): string | undefined => {
    return validateEndDate(value, formData.startedAt)
  }

  const validateMenteesLimit = (value: number | string): string | undefined => {
    const numValue = typeof value === 'string' ? Number(value) : value
    if (numValue < 0) {
      return 'Mentees limit cannot be negative'
    }
    if (!Number.isInteger(numValue)) {
      return 'Mentees limit must be a whole number'
    }
    return undefined
  }

  const errors = useFormValidation(
    [
      ...getCommonValidationRules(formData, touched, validateNameLocal, validateEndDateLocal),
      {
        field: 'menteesLimit',
        shouldValidate: touched.menteesLimit ?? false,
        validator: () => validateMenteesLimit(formData.menteesLimit),
      },
    ],
    [formData, touched, backendErrors]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const allFields = ['name', 'description', 'startedAt', 'endedAt']
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    if (formData.menteesLimit !== undefined && formData.menteesLimit !== null) {
      newTouched.menteesLimit = true
    }
    setTouched(newTouched)

    const nameError = validateName(formData.name, backendErrors.name)
    const descriptionError = validateDescription(formData.description)
    const startDateError = validateStartDate(formData.startedAt)
    const endDateError = validateEndDate(formData.endedAt, formData.startedAt)
    const menteesLimitError =
      touched.menteesLimit || formData.menteesLimit !== undefined
        ? validateMenteesLimit(formData.menteesLimit)
        : undefined

    // Prevent submission if any validation errors exist
    if (nameError || descriptionError || startDateError || endDateError || menteesLimitError) {
      return
    }

    try {
      await onSubmit(e)
    } catch (error) {
      const { validationErrors, hasValidationErrors } = extractGraphQLErrors(error)
      if (hasValidationErrors) {
        setBackendErrors(validationErrors)
      }
    }
  }

  return (
    <FormContainer
      title={title}
      onSubmit={handleSubmit}
      containerClassName="program-form-container"
    >
      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="program-name"
            name="name"
            label="Name"
            placeholder="Enter program name"
            value={formData.name}
            onValueChange={(value) => {
              handleInputChange('name', value)
              setTouched((prev) => ({ ...prev, name: true }))
            }}
            error={errors.name}
            touched={touched.name}
            required
            className="w-full min-w-0 lg:col-span-2"
          />

          <FormTextarea
            id="program-description"
            name="description"
            label="Description"
            placeholder="Enter program description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            onBlur={() => setTouched((prev) => ({ ...prev, description: true }))}
            error={errors.description}
            touched={touched.description}
            required
          />
        </div>
      </section>

      <section className="flex flex-col gap-6 text-gray-600 dark:text-gray-300">
        <div className="config-grid grid gap-6">
          <FormDateInput
            id="program-start-date"
            label="Start Date"
            value={formData.startedAt}
            onValueChange={(value) => {
              handleInputChange('startedAt', value)
              setTouched((prev) => ({ ...prev, startedAt: true }))
            }}
            error={errors.startedAt}
            touched={touched.startedAt}
            required
          />
          <FormDateInput
            id="program-end-date"
            label="End Date"
            value={formData.endedAt}
            onValueChange={(value) => {
              handleInputChange('endedAt', value)
              setTouched((prev) => ({ ...prev, endedAt: true }))
            }}
            error={errors.endedAt}
            touched={touched.endedAt}
            required
            min={formData.startedAt || undefined}
          />
          <FormTextInput
            id="mentees-limit"
            name="menteesLimit"
            type="number"
            label="Mentees Limit"
            placeholder="Enter mentees limit (0 for unlimited)"
            value={formData.menteesLimit?.toString() ?? ''}
            onValueChange={(value) => handleInputChange('menteesLimit', Number(value) || 0)}
            error={errors.menteesLimit}
            touched={touched.menteesLimit}
            min={0}
          />
        </div>
      </section>

      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="program-tags"
            name="tags"
            label="Tags"
            placeholder="javascript, react"
            value={formData.tags}
            onValueChange={(value) => handleInputChange('tags', value)}
          />
          <FormTextInput
            id="program-domains"
            name="domains"
            label="Domains"
            placeholder="AI, Web Development"
            value={formData.domains}
            onValueChange={(value) => handleInputChange('domains', value)}
          />
          {isEdit && (
            <FormTextInput
              id="admin-github-usernames"
              name="adminLogins"
              label="Admin GitHub Usernames"
              placeholder="johndoe, jane-doe"
              value={formData.adminLogins || ''}
              onValueChange={(value) => handleInputChange('adminLogins', value)}
              className="w-full min-w-0 lg:col-span-2"
            />
          )}
        </div>
      </section>

      <FormButtons loading={loading} submitText={submitText} />
    </FormContainer>
  )
}

export default ProgramForm
