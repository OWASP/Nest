'use client'

import { useApolloClient } from '@apollo/client/react'
import type React from 'react'
import { useState, useCallback } from 'react'
import { GetMyProgramsDocument } from 'types/__generated__/programsQueries.generated'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormDateInput } from 'components/forms/shared/FormDateInput'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import {
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
  onSubmit: (e: React.FormEvent) => void
  loading: boolean
  title: string
  submitText?: string
  isEdit?: boolean
  currentProgramKey?: string
}

const ProgramForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
  currentProgramKey,
}: ProgramFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [nameUniquenessError, setNameUniquenessError] = useState<string | undefined>(undefined)
  const client = useApolloClient()

  const handleInputChange = (name: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (name === 'name') {
      setNameUniquenessError(undefined)
    }
  }

  const validateNameLocal = (value: string): string | undefined => {
    return validateName(value, nameUniquenessError)
  }

  const validateNameWithUniqueness = (
    value: string,
    uniquenessError?: string | undefined
  ): string | undefined => {
    return validateName(value, uniquenessError)
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
      {
        field: 'name',
        shouldValidate: touched.name,
        validator: () => validateNameLocal(formData.name),
      },
      {
        field: 'description',
        shouldValidate: touched.description,
        validator: () => validateDescription(formData.description),
      },
      {
        field: 'startedAt',
        shouldValidate: touched.startedAt,
        validator: () => validateStartDate(formData.startedAt),
      },
      {
        field: 'endedAt',
        shouldValidate: touched.endedAt || (touched.startedAt && !!formData.endedAt),
        validator: () => validateEndDateLocal(formData.endedAt),
      },
      {
        field: 'menteesLimit',
        shouldValidate: touched.menteesLimit,
        validator: () => validateMenteesLimit(formData.menteesLimit),
      },
    ],
    [formData, touched, nameUniquenessError]
  )

  const checkNameUniquenessSync = useCallback(
    async (name: string): Promise<string | undefined> => {
      if (!name.trim()) {
        return undefined
      }

      try {
        const { data } = await client.query({
          query: GetMyProgramsDocument,
          variables: { search: name.trim(), page: 1, limit: 100 },
        })

        const programs = data?.myPrograms?.programs || []
        const duplicateProgram = programs.find(
          (program: { name: string; key: string }) =>
            program.name.toLowerCase() === name.trim().toLowerCase() &&
            (!isEdit || program.key !== currentProgramKey)
        )

        if (duplicateProgram) {
          return 'A program with this name already exists'
        }
        return undefined
      } catch {
        // Silently fail uniqueness check - backend will catch it
        return undefined
      }
    },
    [client, isEdit, currentProgramKey]
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

    // Check name uniqueness and capture result before validation
    let uniquenessError: string | undefined
    if (formData.name.trim()) {
      uniquenessError = await checkNameUniquenessSync(formData.name)
      setNameUniquenessError(uniquenessError)
    } else {
      setNameUniquenessError(undefined)
    }

    // Validate all required fields, using the captured uniquenessError
    const nameError = validateNameWithUniqueness(formData.name, uniquenessError)
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

    onSubmit(e)
  }

  return (
    <FormContainer
      title={title}
      onSubmit={handleSubmit}
      containerClassName="program-form-container"
    >
      {/* Basic Information */}
      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="program-name"
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
            label="Description"
            placeholder="Enter program description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            error={errors.description}
            touched={touched.description}
            required
          />
        </div>
      </section>

      {/* Configuration */}
      <section className="flex flex-col gap-6 text-gray-600 dark:text-gray-300">
        <div className="config-grid grid gap-6">
          <FormDateInput
            id="program-start-date"
            label="Start Date"
            value={formData.startedAt}
            onValueChange={(value) => handleInputChange('startedAt', value)}
            error={errors.startedAt}
            touched={touched.startedAt}
            required
          />
          <FormDateInput
            id="program-end-date"
            label="End Date"
            value={formData.endedAt}
            onValueChange={(value) => handleInputChange('endedAt', value)}
            error={errors.endedAt}
            touched={touched.endedAt}
            required
            min={formData.startedAt || undefined}
          />
          <FormTextInput
            id="mentees-limit"
            type="number"
            label="Mentees Limit"
            placeholder="Enter mentees limit (0 for unlimited)"
            value={formData.menteesLimit.toString()}
            onValueChange={(value) => handleInputChange('menteesLimit', Number(value) || 0)}
            error={errors.menteesLimit}
            touched={touched.menteesLimit}
            min={0}
          />
        </div>
      </section>

      {/* Additional Details */}
      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="program-tags"
            label="Tags"
            placeholder="javascript, react"
            value={formData.tags}
            onValueChange={(value) => handleInputChange('tags', value)}
          />
          <FormTextInput
            id="program-domains"
            label="Domains"
            placeholder="AI, Web Development"
            value={formData.domains}
            onValueChange={(value) => handleInputChange('domains', value)}
          />
          {isEdit && (
            <FormTextInput
              id="admin-github-usernames"
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
