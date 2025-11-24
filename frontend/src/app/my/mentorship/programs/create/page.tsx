'use client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'

import { CreateProgramDocument } from 'types/__generated__/programsMutations.generated'
import { ExtendedSession } from 'types/auth'
import { parseCommaSeparated } from 'utils/parser'
import { validateTags } from 'utils/validators'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/ProgramForm'

import { useForm } from 'hooks/useForm'

const CreateProgramPage = () => {
  const router = useRouter()
  const { data: session, status } = useSession()
  const isProjectLeader = (session as ExtendedSession)?.user.isLeader

  const [redirected, setRedirected] = useState(false)

  const [createProgram] = useMutation(CreateProgramDocument)

  useEffect(() => {
    if (status === 'loading') return

    if (!session || !isProjectLeader) {
      addToast({
        title: 'Access Denied',
        description: 'You must be project leader to create a program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.push('/')
      setRedirected(true)
    }
  }, [session, status, router, isProjectLeader])

  const { values, errors, isSubmitting, setValues, handleSubmit } = useForm({
    initialValues: {
      name: '',
      description: '',
      menteesLimit: 5,
      startedAt: '',
      endedAt: '',
      tags: '',
      domains: '',
    },
    validate: (values) => {
      const errors: Record<string, string> = {}
      if (!values.name) errors.name = 'Program name is required'
      if (!values.description) errors.description = 'Description is required'
      if (!values.startedAt) errors.startedAt = 'Start date is required'
      if (!values.endedAt) errors.endedAt = 'End date is required'
      if (new Date(values.startedAt) > new Date(values.endedAt)) {
        errors.startedAt = 'Start date cannot be after end date'
      }

      const tagError = validateTags(values.tags)
      if (tagError) errors.tags = tagError

      return errors
    },
    onSubmit: async (values) => {
      try {
        const input = {
          name: values.name,
          description: values.description,
          menteesLimit: Number(values.menteesLimit),
          startedAt: values.startedAt,
          endedAt: values.endedAt,
          tags: parseCommaSeparated(values.tags),
          domains: parseCommaSeparated(values.domains),
        }

        await createProgram({ variables: { input } })

        addToast({
          description: 'Program created successfully!',
          title: 'Success',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'success',
          variant: 'solid',
        })

        router.push('/my/mentorship')
      } catch (err) {
        let errorMessage = err?.message || 'Unable to complete the requested operation.'
        if (errorMessage.toLowerCase().includes('duplicate') || errorMessage.toLowerCase().includes('unique')) {
          errorMessage = 'A program with this name already exists. Please choose a different name.'
        }

        addToast({
          description: errorMessage,
          title: 'Creation Failed',
          timeout: 3000,
          shouldShowTimeoutProgress: true,
          color: 'danger',
          variant: 'solid',
        })
      }
    },
  })

  if (status === 'loading' || !session || redirected) {
    return <LoadingSpinner />
  }

  return (
    <ProgramForm
      formData={values}
      setFormData={setValues}
      onSubmit={handleSubmit}
      loading={isSubmitting}
      title="Create Program"
      isEdit={false}
      errors={errors}
    />
  )
}

export default CreateProgramPage
