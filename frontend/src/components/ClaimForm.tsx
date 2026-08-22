'use client'

import type React from 'react'
import { useState } from 'react'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import { validateDescription, validateName } from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'

interface ClaimFormProps {
  formData: {
    description: string
    name: string
    sourceText: string
  }
  setFormData: React.Dispatch<
    React.SetStateAction<{
      description: string
      name: string
      sourceText: string
    }>
  >
  onSubmit: (e: React.FormEvent) => Promise<void>
  loading: boolean
  title: string
  submitText?: string
  isSourceTextReadOnly?: boolean
}

const ClaimForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  submitText = 'Create Claim',
  isSourceTextReadOnly = false,
}: ClaimFormProps) => {
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

  const errors = useFormValidation(
    [
      {
        field: 'description',
        shouldValidate: touched.description ?? false,
        validator: () => validateDescription(formData.description),
      },
      {
        field: 'name',
        shouldValidate: touched.name ?? false,
        validator: () => validateName(formData.name),
      },
    ],
    [formData, touched, backendErrors]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const allFields = ['description', 'name']
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    setTouched(newTouched)

    const descriptionError = validateDescription(formData.description)
    const nameError = validateName(formData.name)

    if (descriptionError || nameError) {
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
    <FormContainer title={title} onSubmit={handleSubmit} containerClassName="claim-form-container">
      <section className="flex flex-col gap-2">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="claim-name"
            label="Name"
            placeholder="Enter claim name"
            value={formData.name}
            onValueChange={(value) => {
              handleInputChange('name', value)
              setTouched((prev) => ({ ...prev, name: true }))
            }}
            error={errors.name ?? backendErrors.name}
            touched={touched.name}
            required
            className="w-full min-w-0 lg:col-span-2"
          />

          <FormTextarea
            id="claim-description"
            label="Description"
            placeholder="Enter claim description"
            value={formData.description}
            onChange={(e) => {
              handleInputChange('description', e.target.value)
              setTouched((prev) => ({ ...prev, description: true }))
            }}
            error={errors.description ?? backendErrors.description}
            touched={touched.description}
            required
          />

          <FormTextarea
            id="claim-source-text"
            label="Source Text"
            placeholder={
              isSourceTextReadOnly
                ? 'Selected from your profile'
                : 'Paste the exact text from your profile this claim refers to'
            }
            value={formData.sourceText}
            onChange={(e) => {
              handleInputChange('sourceText', e.target.value)
            }}
            readOnly={isSourceTextReadOnly}
          />
        </div>

        {!isSourceTextReadOnly && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            *Must match your profile text exactly to be highlighted.
          </p>
        )}
      </section>
      <FormButtons loading={loading} submitText={submitText} />
    </FormContainer>
  )
}

export default ClaimForm
