'use client'

import type React from 'react'
import { useCallback, useState } from 'react'
import { FaCheckCircle } from 'react-icons/fa'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import { FormTextarea } from 'components/forms/shared/FormTextarea'

interface FormState {
  organizationName: string
  website: string
  contactEmail: string
  message: string
}

interface TouchedState {
  organizationName: boolean
  website: boolean
  contactEmail: boolean
  message: boolean
}

const initialFormState: FormState = {
  organizationName: '',
  website: '',
  contactEmail: '',
  message: '',
}

const initialTouchedState: TouchedState = {
  organizationName: false,
  website: false,
  contactEmail: false,
  message: false,
}

function validate(form: FormState) {
  const errors: Partial<Record<keyof FormState, string>> = {}

  if (!form.organizationName.trim()) {
    errors.organizationName = 'Organization name is required'
  }

  if (!form.contactEmail.trim()) {
    errors.contactEmail = 'Contact email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.contactEmail)) {
    errors.contactEmail = 'Enter a valid email address'
  }

  if (form.website && !/^https?:\/\/.+\..+/.test(form.website)) {
    errors.website = 'Enter a valid URL (e.g., https://example.com)'
  }

  return errors
}

export default function SponsorApplicationForm() {
  const [form, setForm] = useState<FormState>(initialFormState)
  const [touched, setTouched] = useState<TouchedState>(initialTouchedState)
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)

  const errors = validate(form)
  const hasErrors = Object.keys(errors).length > 0

  const handleFieldChange = useCallback(
    (field: keyof FormState) => (value: string) => {
      setForm((prev) => ({ ...prev, [field]: value }))
    },
    []
  )

  const handleBlur = useCallback(
    (field: keyof FormState) => () => {
      setTouched((prev) => ({ ...prev, [field]: true }))
    },
    []
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    setTouched({
      organizationName: true,
      website: true,
      contactEmail: true,
      message: true,
    })

    if (hasErrors) return

    setLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 1200))
    setLoading(false)
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="rounded-lg bg-gray-100 p-12 text-center shadow-md dark:bg-gray-800">
        <FaCheckCircle className="mx-auto mb-6 h-16 w-16 text-green-500" />
        <h2 className="mb-3 text-2xl font-bold text-gray-800 dark:text-gray-200">
          Application received
        </h2>
        <p className="text-gray-600 dark:text-gray-300">
          Thank you for your interest in sponsoring OWASP Nest. Our team will review your
          application and get in touch.
        </p>
      </div>
    )
  }

  return (
    <FormContainer title="Become a Sponsor" onSubmit={handleSubmit}>
      <p className="-mt-4 mb-2 text-gray-600 dark:text-gray-300">
        Fill out the form below and our team will review your application. We&apos;ll follow up
        within a few business days.
      </p>

      <FormTextInput
        id="organizationName"
        label="Organization name"
        placeholder="Acme Security Corp"
        value={form.organizationName}
        onValueChange={handleFieldChange('organizationName')}
        onBlur={handleBlur('organizationName')}
        error={errors.organizationName}
        touched={touched.organizationName}
        required
      />

      <FormTextInput
        id="website"
        label="Website"
        type="url"
        placeholder="https://example.com"
        value={form.website}
        onValueChange={handleFieldChange('website')}
        onBlur={handleBlur('website')}
        error={errors.website}
        touched={touched.website}
      />

      <FormTextInput
        id="contactEmail"
        label="Contact email"
        type="email"
        placeholder="sponsor@example.com"
        value={form.contactEmail}
        onValueChange={handleFieldChange('contactEmail')}
        onBlur={handleBlur('contactEmail')}
        error={errors.contactEmail}
        touched={touched.contactEmail}
        required
      />

      <FormTextarea
        id="message"
        label="Sponsorship interest / message"
        placeholder="Tell us about your organization and why you'd like to sponsor OWASP Nest..."
        value={form.message}
        onChange={(e) => setForm((prev) => ({ ...prev, message: e.target.value }))}
        error={errors.message}
        touched={touched.message}
        rows={5}
      />

      <FormButtons loading={loading} submitText="Submit Application" />
    </FormContainer>
  )
}
