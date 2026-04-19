'use client'

import { addToast } from '@heroui/toast'
import Link from 'next/link'
import { type ChangeEvent, type FormEvent, useState } from 'react'
import { FaArrowLeft, FaHandshake, FaPaperPlane } from 'react-icons/fa6'
import { API_URL } from 'utils/env.client'
import AnchorTitle from 'components/AnchorTitle'
import SecondaryCard from 'components/SecondaryCard'

interface FormData {
  organizationName: string
  website: string
  contactEmail: string
  message: string
}

interface FormErrors {
  organizationName?: string
  contactEmail?: string
}

const validateForm = (data: FormData): FormErrors => {
  const errors: FormErrors = {}
  if (!data.organizationName.trim()) {
    errors.organizationName = 'Organization name is required.'
  }
  if (!data.contactEmail.trim()) {
    errors.contactEmail = 'Contact email is required.'
  } else if (!/^[^\s@]+@[^\s@.]+\.[^\s@]+$/.test(data.contactEmail)) {
    errors.contactEmail = 'Please enter a valid email address.'
  }
  return errors
}

export default function SponsorApplyPage() {
  const [formData, setFormData] = useState<FormData>({
    organizationName: '',
    website: '',
    contactEmail: '',
    message: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }))
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    const validationErrors = validateForm(formData)
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    setIsSubmitting(true)

    try {
      const payload: Record<string, string> = {}
      payload['contact_email'] = formData.contactEmail
      payload['message'] = formData.message
      payload['organization_name'] = formData.organizationName
      payload['website'] = formData.website
      const baseUrl = (API_URL ?? '').replace(/\/$/, '')
      const response = await fetch(`${baseUrl}/api/v0/sponsors/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        setIsSubmitted(true)
        addToast({
          description: 'Your sponsor application has been submitted for review.',
          title: 'Application Submitted',
          timeout: 5000,
          shouldShowTimeoutProgress: true,
          color: 'success',
          variant: 'solid',
        })
      } else {
        const isJson = response.headers?.get('content-type')?.includes('application/json')
        const errorMessage = isJson
          ? (((await response.json()) as { message?: string }).message ??
            'Failed to submit application. Please try again.')
          : (await response.text()) || 'Failed to submit application. Please try again.'
        addToast({
          description: errorMessage,
          title: 'Submission Failed',
          timeout: 5000,
          shouldShowTimeoutProgress: true,
          color: 'danger',
          variant: 'solid',
        })
      }
    } catch {
      addToast({
        description: 'An unexpected error occurred. Please try again later.',
        title: 'Error',
        timeout: 5000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSubmitted) {
    return (
      <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
        <div className="mx-auto max-w-2xl">
          <SecondaryCard className="text-center">
            <div className="py-12">
              <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                <FaHandshake className="h-10 w-10 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="mb-4 text-2xl font-bold text-gray-800 dark:text-gray-100">
                Thank You for Your Interest!
              </h2>
              <p className="mb-8 text-gray-600 dark:text-gray-400">
                Your sponsor application has been submitted successfully. Our team will review it
                and reach out to you at <strong>{formData.contactEmail}</strong>.
              </p>
              <div className="flex justify-center gap-4">
                <Link
                  href="/sponsors"
                  className="inline-block rounded-lg bg-blue-500 px-6 py-3 font-semibold text-white transition-all duration-200 hover:bg-blue-600"
                >
                  View Sponsors
                </Link>
                <Link
                  href="/"
                  className="inline-block rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-600 transition-all duration-200 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Back to Home
                </Link>
              </div>
            </div>
          </SecondaryCard>
        </div>
      </div>
    )
  }

  return (
    <div className="mt-16 min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/sponsors"
          className="mb-6 inline-flex items-center gap-2 text-sm text-blue-500 transition-colors hover:text-blue-600"
        >
          <FaArrowLeft className="h-3 w-3" />
          Back to Sponsors
        </Link>

        <div className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-gray-800 dark:text-gray-100">
            Become a Sponsor
          </h1>
          <p className="mt-3 text-lg text-gray-500 dark:text-gray-400">
            Support the OWASP Nest project and gain visibility within the global cybersecurity
            community.
          </p>
        </div>

        <SecondaryCard icon={FaPaperPlane} title={<AnchorTitle title="Sponsor Application" />}>
          <form onSubmit={handleSubmit} className="space-y-6" id="sponsor-application-form">
            <div>
              <label
                htmlFor="organizationName"
                className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Organization Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="organizationName"
                name="organizationName"
                value={formData.organizationName}
                onChange={handleChange}
                placeholder="Enter your organization name"
                className={`w-full rounded-lg border bg-white px-4 py-3 text-gray-800 shadow-sm transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none dark:bg-gray-700 dark:text-gray-100 ${
                  errors.organizationName
                    ? 'border-red-400 dark:border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.organizationName && (
                <p className="mt-1 text-sm text-red-500">{errors.organizationName}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="website"
                className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Website URL
              </label>
              <input
                type="url"
                id="website"
                name="website"
                value={formData.website}
                onChange={handleChange}
                placeholder="https://example.com"
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-800 shadow-sm transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
              />
            </div>

            <div>
              <label
                htmlFor="contactEmail"
                className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Contact Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="contactEmail"
                name="contactEmail"
                value={formData.contactEmail}
                onChange={handleChange}
                placeholder="sponsor@example.com"
                className={`w-full rounded-lg border bg-white px-4 py-3 text-gray-800 shadow-sm transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none dark:bg-gray-700 dark:text-gray-100 ${
                  errors.contactEmail
                    ? 'border-red-400 dark:border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errors.contactEmail && (
                <p className="mt-1 text-sm text-red-500">{errors.contactEmail}</p>
              )}
            </div>

            <div>
              <label
                htmlFor="message"
                className="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Sponsorship Interest / Message
              </label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows={5}
                placeholder="Tell us about your organization and why you'd like to sponsor OWASP Nest..."
                className="w-full resize-none rounded-lg border border-gray-300 bg-white px-4 py-3 text-gray-800 shadow-sm transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
              />
            </div>

            <div className="flex items-center justify-end gap-4 pt-2">
              <Link
                href="/sponsors"
                className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-600 transition-all duration-200 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Cancel
              </Link>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-500 px-8 py-3 font-semibold text-white shadow-md transition-all duration-200 hover:bg-blue-600 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <FaPaperPlane className="h-4 w-4" />
                    Submit Application
                  </>
                )}
              </button>
            </div>
          </form>
        </SecondaryCard>

        <SecondaryCard>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <h3 className="mb-2 font-semibold text-gray-700 dark:text-gray-300">
              What happens next?
            </h3>
            <ol className="list-inside list-decimal space-y-1">
              <li>Your application will be reviewed by the OWASP team.</li>
              <li>We'll reach out to discuss sponsorship details and levels.</li>
              <li>Once approved, your organization will be featured on our sponsors page.</li>
            </ol>
          </div>
        </SecondaryCard>
      </div>
    </div>
  )
}
