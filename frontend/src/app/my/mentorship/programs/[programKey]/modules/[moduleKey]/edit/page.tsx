'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { UpdateModuleDocument } from 'types/__generated__/moduleMutations.generated'
import { GetProgramAdminsAndModulesDocument } from 'types/__generated__/moduleQueries.generated'
import type { ExtendedSession } from 'types/auth'
import type { ModuleFormData } from 'types/mentorship'
import { formatDateForInput } from 'utils/dateFormatter'
import { parseCommaSeparated } from 'utils/parser'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/ModuleForm'

const EditModulePage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const router = useRouter()
  const { data: sessionData, status: sessionStatus } = useSession()

  const [formData, setFormData] = useState<ModuleFormData | null>(null)
  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')

  const [updateModule, { loading: mutationLoading }] = useMutation(UpdateModuleDocument)

  const {
    data,
    loading: queryLoading,
    error: queryError,
  } = useQuery(GetProgramAdminsAndModulesDocument, {
    variables: { programKey, moduleKey },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'network-only',
  })

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }

    if (
      queryError ||
      !data?.getProgram ||
      !data?.getModule ||
      sessionStatus === 'unauthenticated'
    ) {
      setAccessStatus('denied')
      return
    }

    const currentUserLogin = (sessionData as ExtendedSession)?.user?.login
    const isAdmin = data.getProgram.admins?.some(
      (admin: { login: string }) => admin.login === currentUserLogin
    )

    if (isAdmin) {
      setAccessStatus('allowed')
    } else {
      setAccessStatus('denied')
      addToast({
        title: 'Access Denied',
        description: 'Only program admins can edit modules.',
        color: 'danger',
        variant: 'solid',
        timeout: 4000,
      })
      setTimeout(() => router.replace(`/my/mentorship/programs/${programKey}`), 1500)
    }
  }, [sessionStatus, sessionData, queryLoading, data, programKey, queryError, router])

  useEffect(() => {
    if (accessStatus === 'allowed' && data?.getModule) {
      const m = data.getModule
      setFormData({
        name: m.name || '',
        description: m.description || '',
        experienceLevel: m.experienceLevel || ExperienceLevelEnum.Beginner,
        startedAt: formatDateForInput(m.startedAt),
        endedAt: formatDateForInput(m.endedAt),
        domains: (m.domains || []).join(', '),
        projectName: m.projectName,
        tags: (m.tags || []).join(', '),
        labels: (m.labels || []).join(', '),
        projectId: m.projectId || '',
        mentorLogins: (m.mentors || []).map((mentor: { login: string }) => mentor.login).join(', '),
      })
    }
  }, [accessStatus, data])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData) return

    try {
      const input = {
        description: formData.description,
        domains: parseCommaSeparated(formData.domains),
        endedAt: formData.endedAt || null,
        experienceLevel: formData.experienceLevel as ExperienceLevelEnum,
        key: moduleKey,
        labels: parseCommaSeparated(formData.labels),
        mentorLogins: parseCommaSeparated(formData.mentorLogins),
        name: formData.name,
        programKey: programKey,
        projectId: formData.projectId,
        projectName: formData.projectName,
        startedAt: formData.startedAt || null,
        tags: parseCommaSeparated(formData.tags),
      }

      await updateModule({ variables: { input } })

      addToast({
        title: 'Module Updated',
        description: 'The module has been successfully updated.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })
      router.push(`/my/mentorship/programs/${programKey}`)
    } catch (err) {
      handleAppError(err)
    }
  }

  if (accessStatus === 'checking' || !formData) {
    return <LoadingSpinner />
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

  return (
    <ModuleForm
      title="Edit Module"
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={mutationLoading}
      submitText="Save"
      isEdit
    />
  )
}

export default EditModulePage
