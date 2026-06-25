'use client'

import type React from 'react'
import { useState } from 'react'
import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormFileInput } from 'components/forms/shared/FormFileInput'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import {
  validateDescription,
  validateFileExtension,
  validateFileSize,
  validateName,
} from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'

const EVIDENCE_ALLOWED_EXTENSIONS = ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg']
const EVIDENCE_MAX_FILE_SIZE_MB = 5

interface EvidenceFormProps {
  formData: {
    description: string
    file: File | null
    name: string
    sourceUrl: string
  }
  setFormData: React.Dispatch<
    React.SetStateAction<{
      description: string
      file: File | null
      name: string
      sourceUrl: string
    }>
  >
  onSubmit: (e: React.FormEvent) => Promise<void>
  loading: boolean
  title: string
  submitText?: string
}

const EvidenceForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  submitText = 'Add Evidence',
}: EvidenceFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})
  const [fileError, setFileError] = useState<string | undefined>()

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

  const handleFilechange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null
    setFormData((prev) => ({ ...prev, file }))
    if (file) {
      const extError = validateFileExtension(file, EVIDENCE_ALLOWED_EXTENSIONS)
      const sizeError = validateFileSize(file, EVIDENCE_MAX_FILE_SIZE_MB)
      setFileError(extError || sizeError || undefined)
    } else {
      setFileError(undefined)
    }
    if (backendErrors['file']) {
      setBackendErrors((prev) => {
        const next = { ...prev }
        delete next['file']
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

    const allFields = ['description', 'name', 'sourceUrl']
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    setTouched(newTouched)

    const descriptionError = validateDescription(formData.description)
    const nameError = validateName(formData.name)

    // Prevent submission if any validation errors exist
    if (descriptionError || nameError) {
      return
    }
    if (!formData.sourceUrl.trim() && !formData.file) {
      setBackendErrors((prev) => ({
        ...prev,
        sourceUrl: 'Either a file or source URL is required.',
      }))
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
      {/* Basic Information */}
      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="evidence-name"
            label="Name"
            placeholder="Enter evidence name"
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
            id="evidence-description"
            label="Description"
            placeholder="Enter evidence description"
            value={formData.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            error={errors.description}
            touched={touched.description}
            required
          />
          <FormTextInput
            id="evidence-source-url"
            label="Source URL"
            placeholder="https://example.com/document.pdf"
            value={formData.sourceUrl}
            onValueChange={(value) => {
              handleInputChange('sourceUrl', value)
              setTouched((prev) => ({ ...prev, sourceUrl: true }))
            }}
            error={errors.sourceUrl || backendErrors.sourceUrl}
            touched={touched.sourceUrl}
            className="w-full min-w-0 lg:col-span-2"
          />
          <FormFileInput
            id="evidence-file"
            label="File (optional)"
            onChange={handleFilechange}
            accept={EVIDENCE_ALLOWED_EXTENSIONS.join(',')}
            selectedFile={formData.file}
            error={fileError}
            touched={true}
          />
        </div>
      </section>
      <FormButtons loading={loading} submitText={submitText} />
    </FormContainer>
  )
}

export default EvidenceForm
