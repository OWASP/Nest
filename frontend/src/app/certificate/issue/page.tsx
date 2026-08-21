'use client'

import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'
import { FaCircleInfo, FaXmark } from 'react-icons/fa6'

import { IssueCertificateDocument } from 'types/__generated__/certificateMutations.generated'
import { ExtendedSession } from 'types/auth'

import { extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'

import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import EntitySelectorInput from 'components/EntitySelectorInput'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormContainer } from 'components/forms/shared/FormContainer'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import { validateRequired } from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'
import LoadingSpinner from 'components/LoadingSpinner'
import UserSelectorInput from 'components/UserSelectorInput'

interface FormData {
  recipientLogins: string[]
  title: string
  message: string
  projectKey: string
  chapterKey: string
}

const INITIAL_FORM: FormData = {
  recipientLogins: [],
  title: '',
  message:
    'In recognition of exceptional contributions to the global OWASP open-source ecosystem and commitment to collaborative innovation.',
  projectKey: '',
  chapterKey: '',
}

const IssueCertificatePage: React.FC = () => {
  const router = useRouter()
  const { data: session, status } = useSession()

  const extendedSession = session as ExtendedSession | undefined
  const isAuthorized = extendedSession?.user?.isLeader || extendedSession?.user?.isChapterLeader

  const [formData, setFormData] = useState<FormData>(INITIAL_FORM)
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [backendErrors, setBackendErrors] = useState<Record<string, string>>({})
  const [showBanner, setShowBanner] = useState(true)

  const [issueCertificate, { loading }] = useMutation(IssueCertificateDocument)

  useEffect(() => {
    if (status === 'loading') return
    if (!session) {
      router.push('/auth/login')
    }
  }, [session, status, router])

  const touch = (field: string) => setTouched((prev) => ({ ...prev, [field]: true }))

  const handleFieldChange = (field: keyof FormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (backendErrors[field]) setBackendErrors(({ [field]: _, ...rest }) => rest)
    touch(field)
  }

  const errors = useFormValidation(
    [
      {
        field: 'recipientLogins',
        shouldValidate: !!touched.recipientLogins,
        validator: () =>
          formData.recipientLogins.length === 0
            ? 'At least one Recipient GitHub Username is required.'
            : undefined,
      },
      {
        field: 'title',
        shouldValidate: !!touched.title,
        validator: () => validateRequired(formData.title, 'Certificate title'),
      },
      {
        field: 'message',
        shouldValidate: !!touched.message,
        validator: () => validateRequired(formData.message, 'Certificate body message'),
      },
    ],
    [formData, touched, backendErrors]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setTouched({ recipientLogins: true, title: true, message: true })

    if (formData.recipientLogins.length === 0 || !formData.title.trim() || !formData.message.trim())
      return

    if (!formData.projectKey.trim() && !formData.chapterKey.trim()) {
      addToast({
        title: 'Validation Error',
        description: 'Please select either a Project Name or a Chapter Name.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      return
    }

    if (formData.projectKey.trim() && formData.chapterKey.trim()) {
      addToast({
        title: 'Validation Error',
        description: 'Please select only one of Project Name or Chapter Name, not both.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      return
    }

    try {
      await issueCertificate({
        variables: {
          inputData: {
            recipientLogins: formData.recipientLogins,
            title: formData.title.trim(),
            message: formData.message.trim(),
            projectKey: formData.projectKey.trim() || null,
            chapterKey: formData.chapterKey.trim() || null,
          },
        },
      })
      const recipients = formData.recipientLogins.map((login) => `@${login}`).join(', ')
      addToast({
        title: 'Success',
        description: `Certificate(s) successfully issued to ${recipients}.`,
        color: 'success',
        variant: 'solid',
        timeout: 4000,
        shouldShowTimeoutProgress: true,
      })
      setFormData(INITIAL_FORM)
      setTouched({})
      setBackendErrors({})
    } catch (err) {
      const { validationErrors, hasValidationErrors } = extractGraphQLErrors(err)
      if (hasValidationErrors) {
        setBackendErrors(validationErrors)
      } else {
        addToast({
          title: 'Failed to Issue Certificate',
          description:
            err instanceof Error ? err.message : 'Unable to complete the requested operation.',
          color: 'danger',
          variant: 'solid',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
        })
      }
    }
  }

  if (status === 'loading') return <LoadingSpinner />

  if (!session || !isAuthorized) {
    return (
      <div className="container mx-auto flex min-h-[50vh] items-center justify-center px-4 py-16">
        <AccessDeniedDisplay
          title="Access Denied"
          message="Only OWASP project leaders or chapter leaders can issue certificates."
        />
      </div>
    )
  }

  const hasEntity = formData.projectKey.trim() || formData.chapterKey.trim()

  return (
    <FormContainer title="Issue Certificate" onSubmit={handleSubmit}>
      {showBanner && (
        <div className="flex items-start justify-between gap-3 rounded-lg border border-l-[3px] border-gray-200 border-l-[#1D7BD7] bg-gray-50 px-4 py-3 dark:border-gray-700 dark:border-l-[#1D7BD7] dark:bg-gray-800/60">
          <div className="flex items-start gap-2.5">
            <FaCircleInfo className="mt-0.5 h-4 w-4 shrink-0 text-[#1D7BD7]" />
            <p className="text-sm text-gray-600 dark:text-gray-300">
              At least one of{' '}
              <span className="font-semibold text-gray-800 dark:text-gray-100">Project Name</span>{' '}
              or{' '}
              <span className="font-semibold text-gray-800 dark:text-gray-100">Chapter Name</span>{' '}
              should be provided to associate this certificate with an OWASP entity.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowBanner(false)}
            aria-label="Dismiss notice"
            className="ml-1 shrink-0 rounded p-1 text-gray-400 transition hover:bg-gray-200 hover:text-gray-600 dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-gray-300"
          >
            <FaXmark className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      <section className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
          <FormTextInput
            id="certificate-title"
            label="Certificate Title"
            placeholder="e.g. Certificate of Acknowledgement"
            value={formData.title}
            onValueChange={(value) => handleFieldChange('title', value)}
            error={errors.title || backendErrors.title}
            touched={touched.title}
            required
          />
          <FormTextarea
            id="certificate-message"
            label="Certificate Body Message"
            placeholder="Write a personalized recognition message for the contributor..."
            value={formData.message}
            onChange={(e) => handleFieldChange('message', e.target.value)}
            error={errors.message}
            touched={touched.message}
            required
          />
        </div>
      </section>

      <section className="flex flex-col gap-3 text-gray-600 dark:text-gray-300">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <EntitySelectorInput
            entityType="project"
            value={formData.projectKey}
            onChange={(key) => setFormData((prev) => ({ ...prev, projectKey: key }))}
            error={
              formData.projectKey && formData.chapterKey
                ? 'Only one of Project or Chapter can be selected.'
                : undefined
            }
          />
          <EntitySelectorInput
            entityType="chapter"
            value={formData.chapterKey}
            onChange={(key) => setFormData((prev) => ({ ...prev, chapterKey: key }))}
            error={
              formData.projectKey && formData.chapterKey
                ? 'Only one of Project or Chapter can be selected.'
                : undefined
            }
          />
        </div>
      </section>

      <UserSelectorInput
        logins={formData.recipientLogins}
        onChange={(logins) => {
          setFormData((prev) => ({ ...prev, recipientLogins: logins }))
          touch('recipientLogins')
        }}
        projectKey={formData.projectKey}
        chapterKey={formData.chapterKey}
        disabled={!hasEntity}
        error={
          errors.recipientLogins || backendErrors.recipientLogins || backendErrors.recipientLogin
        }
        touched={touched.recipientLogins}
      />

      <FormButtons loading={loading} submitText="Issue Certificate" />
    </FormContainer>
  )
}

export default IssueCertificatePage
