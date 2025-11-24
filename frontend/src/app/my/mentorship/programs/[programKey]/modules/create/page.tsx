'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { CreateModuleDocument } from 'types/__generated__/moduleMutations.generated'
import {
  GetProgramAdminDetailsDocument,
  GetProgramAndModulesDocument,
} from 'types/__generated__/programsQueries.generated'
import type { ExtendedSession } from 'types/auth'
import { parseCommaSeparated } from 'utils/parser'
import { validateTags } from 'utils/validators'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/ModuleForm'
import { useForm } from 'hooks/useForm'

const CreateModulePage = () => {
  const router = useRouter()
  const params = useParams<{ programKey: string }>()
  const { data: sessionData, status: sessionStatus } = useSession()

  const [createModule, { loading: mutationLoading }] = useMutation(CreateModuleDocument)

  const {
    data: programData,
    loading: queryLoading,
    error: queryError,
  } = useQuery(GetProgramAdminDetailsDocument, {
    variables: { programKey: params.programKey },
    skip: !params.programKey,
    fetchPolicy: 'network-only',
  })

  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')

  const validate = (values: any) => {
    const errors: Record<string, string> = {}

    if (!values.name) errors.name = 'Name is required'
    if (!values.description) errors.description = 'Description is required'
    if (!values.startedAt) errors.startedAt = 'Start date is required'
    if (!values.endedAt) errors.endedAt = 'End date is required'
    if (!values.projectId) errors.projectId = 'Please select a valid project from the list.'

    if (values.startedAt && values.endedAt) {
      if (new Date(values.startedAt) > new Date(values.endedAt)) {
        errors.startedAt = 'Start date cannot be after end date'
      }
    }

    const tagError = validateTags(values.tags)
    if (tagError) errors.tags = tagError

    return errors
  }

  const { values, errors, isSubmitting, handleSubmit, setValues, setErrors } = useForm({
    initialValues: {
      description: '',
      domains: '',
      endedAt: '',
      experienceLevel: ExperienceLevelEnum.Beginner,
      labels: '',
      mentorLogins: '',
      name: '',
      projectId: '',
      projectName: '',
      startedAt: '',
      tags: '',
    },
    validate,
    onSubmit: async (values) => {
      try {
        const input = {
          description: values.description,
          domains: parseCommaSeparated(values.domains),
          endedAt: values.endedAt || null,
          experienceLevel: values.experienceLevel,
          labels: parseCommaSeparated(values.labels),
          mentorLogins: parseCommaSeparated(values.mentorLogins),
          name: values.name,
          programKey: params.programKey,
          projectId: values.projectId,
          projectName: values.projectName,
          startedAt: values.startedAt || null,
          tags: parseCommaSeparated(values.tags),
        }

        await createModule({
          variables: { input },
          update: (cache, { data: mutationData }) => {
            const created = mutationData?.createModule
            if (!created) return
            try {
              const existing = cache.readQuery({
                query: GetProgramAndModulesDocument,
                variables: { programKey: params.programKey },
              })
              if (existing?.getProgram && existing?.getProgramModules) {
                cache.writeQuery({
                  query: GetProgramAndModulesDocument,
                  variables: { programKey: params.programKey },
                  data: {
                    getProgram: existing.getProgram,
                    getProgramModules: [created, ...existing.getProgramModules],
                  },
                })
              }
            } catch (_err) {
              handleAppError(_err)
              return
            }
          },
        })

        addToast({
          title: 'Module Created',
          description: 'The new module has been successfully created.',
          color: 'success',
          variant: 'solid',
          timeout: 3000,
        })

        router.push(`/my/mentorship/programs/${params.programKey}`)
      } catch (err: any) {
        addToast({
          title: 'Creation Failed',
          description: err.message || 'Something went wrong while creating the module.',
          color: 'danger',
          variant: 'solid',
          timeout: 4000,
        })
      }
    },
  })

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }

    if (queryError || !programData?.getProgram || sessionStatus === 'unauthenticated') {
      setAccessStatus('denied')
      return
    }

    const currentUserLogin = (sessionData as ExtendedSession)?.user?.login
    const isAdmin = programData.getProgram.admins?.some(
      (admin: { login: string }) => admin.login === currentUserLogin
    )

    if (isAdmin) {
      setAccessStatus('allowed')
    } else {
      setAccessStatus('denied')
      addToast({
        title: 'Access Denied',
        description: 'Only program admins can create modules.',
        color: 'danger',
        variant: 'solid',
        timeout: 4000,
      })
      setTimeout(() => router.replace('/my/mentorship'), 1500)
    }
  }, [sessionStatus, sessionData, queryLoading, programData, params.programKey, queryError, router])

  if (accessStatus === 'checking') {
    return <LoadingSpinner />
  }

  if (accessStatus === 'denied') {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to perform this action. You will be redirected."
      />
    )
  }

  return (
    <ModuleForm
      title="Create New Module"
      submitText="Create Module"
      formData={values}
      setFormData={setValues}
      onSubmit={handleSubmit}
      loading={isSubmitting}
      isEdit={false}
      errors={errors}
    />
  )
}

export default CreateModulePage
