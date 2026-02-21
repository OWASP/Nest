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
import { formatDateForInput } from 'utils/dateFormatter'
import { type FieldErrors, extractFieldErrors } from 'utils/helpers/handleGraphQLError'
import { parseCommaSeparated } from 'utils/parser'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/ModuleForm'

const CreateModulePage = () => {
  const router = useRouter()
  const { programKey } = useParams<{ programKey: string }>()
  const { data: sessionData, status: sessionStatus } = useSession()

  const [createModule, { loading: mutationLoading }] = useMutation(CreateModuleDocument)

  const {
    data: programData,
    loading: queryLoading,
    error: queryError,
  } = useQuery(GetProgramAdminDetailsDocument, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'network-only',
  })

  const [formData, setFormData] = useState<{
    description: string
    domains: string
    endedAt: string
    experienceLevel: string
    labels: string
    mentorLogins: string
    name: string
    projectId: string
    projectName: string
    startedAt: string
    tags: string
  }>({
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
  })

  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')
  const [mutationErrors, setMutationErrors] = useState<FieldErrors>({})

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
  }, [sessionStatus, sessionData, queryLoading, programData, programKey, queryError, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setMutationErrors({})

    try {
      const input = {
        description: formData.description,
        domains: parseCommaSeparated(formData.domains),
        endedAt: formData.endedAt,
        experienceLevel: formData.experienceLevel as ExperienceLevelEnum,
        labels: parseCommaSeparated(formData.labels),
        mentorLogins: parseCommaSeparated(formData.mentorLogins),
        name: formData.name,
        programKey: programKey,
        projectId: formData.projectId,
        projectName: formData.projectName,
        startedAt: formData.startedAt,
        tags: parseCommaSeparated(formData.tags),
      }

      await createModule({
        awaitRefetchQueries: true,
        refetchQueries: [{ query: GetProgramAndModulesDocument, variables: { programKey } }],
        variables: { input },
      })

      addToast({
        title: 'Module Created',
        description: 'The new module has been successfully created.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })

      router.push(`/my/mentorship/programs/${programKey}`)
    } catch (error) {
      const { fieldErrors, hasFieldErrors, unmappedErrors } = extractFieldErrors(error)
      if (hasFieldErrors) {
        setMutationErrors(fieldErrors)
      } else if (unmappedErrors.length > 0) {
        setMutationErrors({ name: unmappedErrors[0] })
      } else {
        handleAppError(error)
      }
    }
  }

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
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={mutationLoading}
      isEdit={false}
      mutationErrors={mutationErrors}
      minDate={
        programData?.getProgram?.startedAt
          ? formatDateForInput(programData.getProgram.startedAt)
          : undefined
      }
      maxDate={
        programData?.getProgram?.endedAt
          ? formatDateForInput(programData.getProgram.endedAt)
          : undefined
      }
    />
  )
}

export default CreateModulePage
