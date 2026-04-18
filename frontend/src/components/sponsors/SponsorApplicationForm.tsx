'use client'

import Link from 'next/link'
import type React from 'react'
import { useCallback, useState } from 'react'
import { FaCheckCircle } from 'react-icons/fa'
import { OWASP_NEST_SLACK_CHANNEL_URL } from 'utils/constants'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'

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

function isProbablyEmail(value: string): boolean {
  // Keep it linear-time to avoid regex backtracking warnings.
  const email = value.trim()
  if (!email || email.includes(' ') || email.length > 254) return false
  //check valid email address
  const at = email.indexOf('@')
  if (at <= 0 || at !== email.lastIndexOf('@') || at === email.length - 1) return false

  const domain = email.slice(at + 1)
  const dot = domain.indexOf('.')
  if (dot <= 0 || dot === domain.length - 1) return false

  return true
}

function isHttpUrl(value: string): boolean {
  const raw = value.trim()
  if (!raw) return false

  try {
    const url = new URL(raw)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

function validate(form: FormState) {
  const errors: Partial<Record<keyof FormState, string>> = {}

  if (!form.organizationName.trim()) {
    errors.organizationName = 'Organization name is required'
  }

  if (!form.contactEmail.trim()) {
    errors.contactEmail = 'Contact email is required'
  } else if (!isProbablyEmail(form.contactEmail)) {
    errors.contactEmail = 'Enter a valid email address'
  }

  if (form.website && !isHttpUrl(form.website)) {
    errors.website = 'Enter a valid URL (e.g., https://example.com)'
  }

  return errors
}

export default function SponsorApplicationForm() {
  const [form, setForm] = useState<FormState>(initialFormState)
  const [touched, setTouched] = useState<TouchedState>(initialTouchedState)
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const errors = validate(form)

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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    setTouched({
      organizationName: true,
      website: true,
      contactEmail: true,
      message: true,
    })

    const fd = new FormData(e.currentTarget)
    const current: FormState = {
      organizationName: String(fd.get('organizationName') ?? ''),
      website: String(fd.get('website') ?? ''),
      contactEmail: String(fd.get('contactEmail') ?? ''),
      message: String(fd.get('message') ?? ''),
    }
    setForm(current)

    if (Object.keys(validate(current)).length > 0) {
      return
    }

    setLoading(true)
    setServerError(null)

    try {
      const res = await fetch('/api/v0/sponsors/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          Object.fromEntries([
            ['organization_name', current.organizationName.trim()],
            ['website', current.website.trim()],
            ['contact_email', current.contactEmail.trim()],
            ['message', current.message.trim()],
          ])
        ),
      })

      if (res.ok) {
        setSubmitted(true)
      } else {
        const data = (await res.json()) as { message?: string }
        setServerError(data.message ?? 'Something went wrong. Please try again.')
      }
    } catch {
      setServerError('Could not reach the server. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="rounded-lg bg-gray-100 p-8 shadow-md sm:p-10 dark:bg-gray-800">
        <div className="mx-auto max-w-xl text-center">
          <FaCheckCircle className="mx-auto mb-5 h-14 w-14 text-green-600 dark:text-green-500" />
          <h2 className="mb-2 text-2xl font-semibold text-gray-900 dark:text-white">
            Application received
          </h2>
          <p className="mb-6 text-gray-600 dark:text-gray-400">
            Thanks for your interest in sponsoring OWASP Nest. The team will review your application
            and follow up via the email you provided.
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Want to introduce yourself sooner? Reach out in{' '}
            <a
              href={OWASP_NEST_SLACK_CHANNEL_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-blue-600 underline-offset-2 hover:underline dark:text-blue-400"
            >
              #project-nest
            </a>{' '}
            on Slack.
          </p>
          <p className="mt-6">
            <Link
              href="/sponsors"
              className="text-sm font-medium text-blue-600 underline-offset-2 hover:underline dark:text-blue-400"
            >
              &larr; Back to sponsors
            </Link>
          </p>
        </div>
      </div>
    )
  }

  return (
    <section
      className="rounded-lg bg-gray-100 p-6 shadow-md sm:p-8 dark:bg-gray-800"
      aria-labelledby="sponsor-apply-form-heading"
    >
      <h2
        id="sponsor-apply-form-heading"
        className="mb-2 text-xl font-semibold text-gray-900 sm:text-2xl dark:text-white"
      >
        Application details
      </h2>
      <p className="mb-8 text-sm text-gray-600 dark:text-gray-400">
        Required fields are marked. The Nest team reviews applications via Django Admin and will
        follow up by email.
      </p>

      {serverError && (
        <p className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
          {serverError}
        </p>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="flex flex-col gap-6 rounded-lg bg-gray-200 p-6 sm:p-8 dark:bg-gray-700">
          <FormTextInput
            id="organizationName"
            name="organizationName"
            label="Organization name"
            placeholder="Acme Security Corp"
            value={form.organizationName}
            onValueChange={handleFieldChange('organizationName')}
            onBlur={handleBlur('organizationName')}
            error={errors.organizationName}
            touched={touched.organizationName}
            required
            autoComplete="organization"
          />

          <FormTextInput
            id="website"
            name="website"
            label="Website"
            type="url"
            placeholder="https://example.com"
            value={form.website}
            onValueChange={handleFieldChange('website')}
            onBlur={handleBlur('website')}
            error={errors.website}
            touched={touched.website}
            autoComplete="url"
          />

          <FormTextInput
            id="contactEmail"
            name="contactEmail"
            label="Contact email"
            type="email"
            placeholder="sponsor@example.com"
            value={form.contactEmail}
            onValueChange={handleFieldChange('contactEmail')}
            onBlur={handleBlur('contactEmail')}
            error={errors.contactEmail}
            touched={touched.contactEmail}
            required
            autoComplete="email"
          />

          <FormTextarea
            id="message"
            name="message"
            label="Sponsorship interest / message"
            placeholder="Tell us about your organization and why you'd like to sponsor OWASP Nest..."
            value={form.message}
            onChange={(e) => setForm((prev) => ({ ...prev, message: e.target.value }))}
            onBlur={handleBlur('message')}
            error={errors.message}
            touched={touched.message}
            rows={5}
          />

          <FormButtons loading={loading} submitText="Submit application" />
        </div>
      </form>
    </section>
  )
}
