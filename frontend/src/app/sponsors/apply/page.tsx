'use client'

import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import type React from 'react'
import { useState } from 'react'
import { FaCheck, FaExclamation } from 'react-icons/fa6'
import { CREATE_SPONSOR_APPLICATION } from 'server/mutations/sponsorMutations'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import PageLayout from 'components/PageLayout'

type FormStatus = 'idle' | 'loading' | 'success' | 'error'

// RFC-compliant email regex: explicit character classes, no backtracking ambiguity, linear complexity
const EMAIL_REGEX =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/

interface FormData {
  name: string
  contactEmail: string
  website: string
  sponsorshipInterest: string
}

const SponsorApplyPage = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    contactEmail: '',
    website: '',
    sponsorshipInterest: '',
  })

  const [status, setStatus] = useState<FormStatus>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [touched, setTouched] = useState<{ [K in keyof FormData]?: boolean }>({})

  const [createSponsorApplication, { loading: mutationLoading }] = useMutation(
    CREATE_SPONSOR_APPLICATION
  )

  const isNameEmpty = (): boolean => formData.name.trim() === ''
  const isEmailEmpty = (): boolean => formData.contactEmail.trim() === ''
  const isValidEmail = (): boolean => EMAIL_REGEX.test(formData.contactEmail)
  const isInvalidEmail = (): boolean => !isValidEmail()
  const isInterestEmpty = (): boolean => formData.sponsorshipInterest.trim() === ''
  const getNameError = (): string | undefined => {
    if (!touched.name) return undefined
    if (isNameEmpty()) return 'Organization name is required'
    return undefined
  }

  const getEmailError = (): string | undefined => {
    if (!touched.contactEmail) return undefined
    if (isEmailEmpty()) return 'Contact email is required'
    if (isInvalidEmail()) return 'Please enter a valid email address'
    return undefined
  }

  const getInterestError = (): string | undefined => {
    if (!touched.sponsorshipInterest) return undefined
    if (isInterestEmpty()) return 'Please tell us about your sponsorship interest'
    return undefined
  }

  const handleInputChange = (name: keyof FormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setTouched((prev) => ({ ...prev, [name]: true }))
  }

  const validateForm = (): boolean => {
    if (isNameEmpty()) {
      setErrorMessage('Organization name is required')
      return false
    }
    if (isEmailEmpty()) {
      setErrorMessage('Contact email is required')
      return false
    }
    if (isInvalidEmail()) {
      setErrorMessage('Please enter a valid email address')
      return false
    }
    if (isInterestEmpty()) {
      setErrorMessage('Please tell us about your sponsorship interest')
      return false
    }
    setErrorMessage('')
    return true
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setErrorMessage('')

    if (!validateForm()) {
      setStatus('error')
      return
    }

    setStatus('loading')

    try {
      const { data } = await createSponsorApplication({
        variables: {
          name: formData.name.trim(),
          contactEmail: formData.contactEmail.trim(),
          website: formData.website.trim() || null,
          sponsorshipInterest: formData.sponsorshipInterest.trim(),
        },
      })

      if (data?.createSponsorApplication?.ok) {
        setStatus('success')
        setFormData({
          name: '',
          contactEmail: '',
          website: '',
          sponsorshipInterest: '',
        })
        addToast({
          title: 'Application Submitted',
          description: 'Thank you for your interest. We will review your application shortly.',
          color: 'success',
          variant: 'solid',
          timeout: 4000,
        })
      } else {
        setStatus('error')
        setErrorMessage(data?.createSponsorApplication?.message || 'Failed to submit application')
      }
    } catch (error) {
      setStatus('error')
      setErrorMessage(
        error instanceof Error ? error.message : 'An error occurred while submitting the form'
      )
    }
  }

  return (
    <PageLayout title="Sponsor Application" path="/sponsors/apply">
      <div className="flex min-h-screen flex-col items-center justify-center bg-white text-gray-600 dark:bg-[#212529] dark:text-gray-300">
        <div className="flex w-full max-w-2xl flex-col justify-center">
          <h1 className="mb-4 text-center text-4xl font-bold tracking-tight text-gray-900 dark:text-white">
            Become a Sponsor
          </h1>
          <p className="mb-8 text-center text-lg text-gray-600 dark:text-gray-300">
            We appreciate your interest in supporting OWASP Nest. Please fill out this form to apply
            for a sponsorship opportunity.
          </p>
          {status === 'success' ? (
            <div className="rounded-lg border border-green-200 bg-green-50 p-8 text-center dark:border-green-900/30 dark:bg-green-900/10">
              <div className="mb-4 flex justify-center">
                <div className="rounded-full bg-green-100 p-4 dark:bg-green-900/30">
                  <FaCheck className="h-8 w-8 text-green-600 dark:text-green-400" />
                </div>
              </div>
              <h2 className="mb-2 text-2xl font-bold text-green-900 dark:text-green-300">
                Application Submitted Successfully!
              </h2>
              <p className="mb-6 text-green-800 dark:text-green-400">
                Thank you for your interest in sponsoring OWASP Nest. We have received your
                application and will review it shortly. Our team will contact you at the email
                address provided.
              </p>
            </div>
          ) : (
            <FormContainer
              title="Sponsor Application"
              onSubmit={handleSubmit}
              containerClassName="shadow-none border-none bg-transparent p-0"
            >
              {status === 'error' && errorMessage && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-900/30 dark:bg-red-900/10">
                  <div className="flex items-start gap-3">
                    <FaExclamation className="mt-0.5 h-5 w-5 shrink-0 text-red-600 dark:text-red-400" />
                    <p className="text-red-800 dark:text-red-300">{errorMessage}</p>
                  </div>
                </div>
              )}
              <FormTextInput
                id="name"
                label="Organization Name"
                value={formData.name}
                onValueChange={(v) => handleInputChange('name', v)}
                error={getNameError()}
                touched={touched.name}
                required
                placeholder="Your organization name"
              />
              <FormTextInput
                id="contactEmail"
                type="email"
                label="Contact Email"
                value={formData.contactEmail}
                onValueChange={(v) => handleInputChange('contactEmail', v)}
                error={getEmailError()}
                touched={touched.contactEmail}
                required
                placeholder="your.email@example.com"
              />
              <FormTextInput
                id="website"
                type="url"
                label="Organization Website"
                value={formData.website}
                onValueChange={(v) => handleInputChange('website', v)}
                error={undefined}
                touched={touched.website}
                placeholder="https://example.com"
              />
              <FormTextarea
                id="sponsorshipInterest"
                label="Sponsorship Interest / Message"
                value={formData.sponsorshipInterest}
                onChange={(e) => handleInputChange('sponsorshipInterest', e.target.value)}
                error={getInterestError()}
                touched={touched.sponsorshipInterest}
                required
                placeholder="Tell us about your interest in sponsoring OWASP Nest..."
                rows={5}
              />
              <FormButtons loading={mutationLoading} submitText="Submit Application" />
            </FormContainer>
          )}
        </div>
      </div>
    </PageLayout>
  )
}

export default SponsorApplyPage
