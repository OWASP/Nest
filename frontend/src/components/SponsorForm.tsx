'use client'

import React, { useState } from 'react'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import {
  validateName,
  validateWebsite,
  validateContactEmail,
  validateMessage,
} from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'

interface SponsorFormProps {
  formData: {
    name: string
    website: string
    contactEmail: string
    message: string
  }
  setFormData: React.Dispatch<React.SetStateAction<SponsorFormProps['formData']>>
  onSubmit: (e: React.FormEvent) => void
  loading: boolean
  title: string
  submitText?: string
}

const SponsorForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  submitText = 'Submit',
}: SponsorFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const handleInputChange = (name: keyof SponsorFormProps['formData'], value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const errors = useFormValidation(
    [
      {
        field: 'name',
        shouldValidate: touched.name ?? false,
        validator: () => validateName(formData.name),
      },
      {
        field: 'website',
        shouldValidate: touched.website ?? false,
        validator: () => validateWebsite(formData.website),
      },
      {
        field: 'contactEmail',
        shouldValidate: touched.contactEmail ?? false,
        validator: () => validateContactEmail(formData.contactEmail),
      },
      {
        field: 'message',
        shouldValidate: touched.message ?? false,
        validator: () => validateMessage(formData.message),
      },
    ],
    [formData, touched]
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const nextTouched = {
      name: true,
      website: true,
      contactEmail: true,
      message: true,
    }
    setTouched(nextTouched)

    if (
      validateName(formData.name) ||
      validateWebsite(formData.website) ||
      validateContactEmail(formData.contactEmail) ||
      validateMessage(formData.message)
    ) {
      return
    }

    onSubmit(e)
  }

  return (
    <FormContainer
      title={title}
      onSubmit={handleSubmit}
      containerClassName="sponsor-form-container"
    >
      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="sponsor-name"
            label="Name"
            placeholder="Enter sponsor name"
            value={formData.name}
            onValueChange={(value) => {
              handleInputChange('name', value)
              setTouched((prev) => ({ ...prev, name: true }))
            }}
            error={errors.name}
            touched={touched.name}
            required
          />

          <FormTextInput
            id="sponsor-website"
            type="url"
            label="Website"
            placeholder="https://example.com"
            value={formData.website}
            onValueChange={(value) => {
              handleInputChange('website', value)
              setTouched((prev) => ({ ...prev, website: true }))
            }}
            error={errors.website}
            touched={touched.website}
            required
          />

          <FormTextInput
            id="sponsor-contact-email"
            type="email"
            label="Contact Email"
            placeholder="name@example.com"
            value={formData.contactEmail}
            onValueChange={(value) => {
              handleInputChange('contactEmail', value)
              setTouched((prev) => ({ ...prev, contactEmail: true }))
            }}
            error={errors.contactEmail}
            touched={touched.contactEmail}
            required
            className="w-full min-w-0 lg:col-span-2"
          />

          <FormTextarea
            id="sponsor-message"
            label="Message"
            placeholder="Tell us about your organization and sponsorship interest"
            value={formData.message}
            onChange={(e) => {
              handleInputChange('message', e.target.value)
              setTouched((prev) => ({ ...prev, message: true }))
            }}
            error={errors.message}
            touched={touched.message}
            rows={6}
            required
          />
        </div>
      </section>

      <FormButtons loading={loading} submitText={submitText} />
    </FormContainer>
  )
}

export default SponsorForm
