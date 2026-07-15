'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import type { UpdateModuleInput } from 'types/__generated__/graphql'
import { UpdateModuleDocument } from 'types/__generated__/moduleMutations.generated'
import { GetManagementProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import { GetManagementProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import type { ExtendedSession } from 'types/auth'
import type { ModuleFormData } from 'types/mentorship'
import { formatDateForInput } from 'utils/dateFormatter'
import { type ValidationErrors, extractGraphQLErrors } from 'utils/helpers/handleGraphQLError'
import { parseCommaSeparated } from 'utils/parser'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/ModuleForm'

const EditModulePage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const router = useRouter()
  const { data: sessionData, status: sessionStatus } = useSession() as {
    data: ExtendedSession | null
    status: string
  }

  const [formData, setFormData] = useState<ModuleFormData | null>(null)
  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({})

  const [updateModule, { loading: mutationLoading }] = useMutation(UpdateModuleDocument)

  const {
    data,
    loading: queryLoading,
    error: queryError,
  } = useQuery(GetManagementProgramAdminsAndModulesDocument, {
    variables: { programKey, moduleKey },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'network-only',
  })

  const currentUserLogin = sessionData?.user?.login

  const isAdmin = useMemo(
    () =>
      data?.managementProgram?.admins?.some(
        (admin: { login: string }) => admin.login === currentUserLogin
      ),
    [data?.managementProgram?.admins, currentUserLogin]
  )

  const isMentor = useMemo(
    () =>
      data?.managementModule?.mentors?.some(
        (mentor: { login: string }) => mentor.login === currentUserLogin
      ),
    [data?.managementModule?.mentors, currentUserLogin]
  )

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }

    if (
      queryError ||
      !data?.managementProgram ||
      !data?.managementModule ||
      sessionStatus === 'unauthenticated'
    ) {
      setAccessStatus('denied')
      return
    }

    if (isAdmin || isMentor) {
      setAccessStatus('allowed')
    } else {
      setAccessStatus('denied')
      addToast({
        title: 'Access Denied',
        description: 'Only program admins and module mentors can edit this module.',
        color: 'danger',
        variant: 'solid',
        timeout: 4000,
      })
      setTimeout(() => router.replace(`/my/mentorship/programs/${programKey}`), 1500)
    }
  }, [sessionStatus, queryLoading, queryError, data, programKey, router, isAdmin, isMentor])

  useEffect(() => {
    if (accessStatus === 'allowed' && data?.managementModule) {
      const m = data.managementModule
      setFormData({
        description: m.description || '',
        domains: (m.domains || []).join(', '),
        endedAt: formatDateForInput(m.endedAt),
        experienceLevel: m.experienceLevel || ExperienceLevelEnum.Beginner,
        labels: (m.labels || []).join(', '),
        menteeCanManageDeadlines: m.menteeCanManageDeadlines ?? false,
        mentorLogins: (m.mentors || []).map((mentor: { login: string }) => mentor.login).join(', '),
        name: m.name || '',
        projectId: m.projectId || '',
        projectName: m.projectName || '',
        startedAt: formatDateForInput(m.startedAt),
        tags: (m.tags || []).join(', '),
      })
    }
  }, [accessStatus, data])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData) return
    setValidationErrors({})

    try {
      const input: UpdateModuleInput = {
        description: formData!.description,
        domains: parseCommaSeparated(formData!.domains),
        endedAt: formData!.endedAt || '',
        experienceLevel: formData!.experienceLevel as ExperienceLevelEnum,
        key: moduleKey,
        labels: parseCommaSeparated(formData!.labels),
        menteeCanManageDeadlines: formData!.menteeCanManageDeadlines,
        name: formData!.name,
        programKey: programKey,
        projectId: formData!.projectId,
        projectName: formData!.projectName,
        startedAt: formData!.startedAt || '',
        tags: parseCommaSeparated(formData!.tags),
      }

      if (isAdmin) {
        input.mentorLogins = parseCommaSeparated(formData!.mentorLogins)
      }

      const result = await updateModule({
        awaitRefetchQueries: true,
        refetchQueries: [
          { query: GetManagementProgramAndModulesDocument, variables: { programKey } },
        ],
        variables: { input },
      })
      const updatedModuleKey = result.data?.updateModule?.key || moduleKey

      addToast({
        title: 'Module Updated',
        description: 'The module has been successfully updated.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })
      router.push(`/my/mentorship/programs/${programKey}/modules/${updatedModuleKey}`)
    } catch (err) {
      const {
        validationErrors: errors,
        hasValidationErrors,
        unmappedErrors,
      } = extractGraphQLErrors(err)
      if (hasValidationErrors) {
        setValidationErrors(errors)
      } else if (unmappedErrors.length > 0) {
        setValidationErrors({ name: unmappedErrors[0] })
      } else {
        handleAppError(err)
      }
    }
  }

  if (accessStatus === 'denied') {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to edit this module. You will be redirected."
      />
    )
  }

  if (accessStatus === 'checking' || !formData) {
    return <LoadingSpinner />
  }

  return (
    <ModuleForm
      title="Edit Module"
      formData={formData}
      setFormData={setFormData as React.Dispatch<React.SetStateAction<ModuleFormData>>}
      onSubmit={handleSubmit}
      loading={mutationLoading}
      submitText="Save"
      isEdit
      validationErrors={validationErrors}
      minDate={
        data?.managementProgram?.startedAt
          ? formatDateForInput(data.managementProgram.startedAt)
          : undefined
      }
      maxDate={
        data?.managementProgram?.endedAt
          ? formatDateForInput(data.managementProgram.endedAt)
          : undefined
      }
    />
  )
}

export default EditModulePage
