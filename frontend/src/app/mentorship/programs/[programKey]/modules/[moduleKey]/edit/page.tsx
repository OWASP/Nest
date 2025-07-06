'use client'

import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useParams, useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react'
import type React from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROGRAM_ADMINS_AND_MODULES, UPDATE_MODULE } from 'server/queries/moduleQueries'
import { SessionWithRole } from 'types/program'
import { formatDateForInput } from 'utils/dateFormatter'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/mainmoduleCard'

const EditModulePage = () => {
  const { programKey, moduleKey } = useParams() as { programKey: string; moduleKey: string }
  const router = useRouter()
  const { data: sessionData, status: sessionStatus } = useSession()
  const currentUserLogin = (sessionData as SessionWithRole)?.user?.username || ''

  type ModuleFormData = {
    key: string
    name: string
    description: string
    experienceLevel: string
    startedAt: string
    endedAt: string
    domains: string
    tags: string
    projectId: string
    mentorLogins: string
  }

  const [formData, setFormData] = useState<ModuleFormData | null>(null)
  const [checkedAccess, setCheckedAccess] = useState(false)
  const [hasAccess, setHasAccess] = useState(false)

  const [updateModule, { loading: mutationLoading }] = useMutation(UPDATE_MODULE)

  const {
    data,
    loading: queryLoading,
    error,
  } = useQuery(GET_PROGRAM_ADMINS_AND_MODULES, {
    variables: { programKey, moduleKey },
    skip: !programKey || !moduleKey,
  })

  useEffect(() => {
    if (sessionStatus !== 'authenticated' || queryLoading) return

    const programAdmins = data?.program?.admins || []
    const isAdmin = programAdmins.some(
      (admin: { login: string }) => admin.login === currentUserLogin
    )

    setHasAccess(isAdmin)
    setCheckedAccess(true)

    if (!isAdmin) {
      addToast({
        title: 'Access Denied',
        description: 'Only program admins can edit modules.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.replace(`/mentorship/programs/${programKey}`)
    }
  }, [sessionStatus, queryLoading, data, currentUserLogin, programKey, router])

  useEffect(() => {
    if (data?.getModule) {
      const m = data.getModule
      setFormData({
        key: moduleKey,
        name: m.name,
        description: m.description,
        experienceLevel: m.experienceLevel || 'BEGINNER',
        startedAt: formatDateForInput(m.startedAt),
        endedAt: formatDateForInput(m.endedAt),
        domains: m.domains?.join(', ') || '',
        tags: m.tags?.join(', ') || '',
        projectId: m.projectId || '',
        mentorLogins: m.mentors?.map((mentor: { login: string }) => mentor.login).join(', ') || '',
      })
    } else if (error) {
      handleAppError(error)
    }
  }, [data, error, moduleKey])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData) return

    const input = {
      key: moduleKey,
      name: formData.name,
      description: formData.description,
      experienceLevel: formData.experienceLevel,
      startedAt: formData.startedAt || null,
      endedAt: formData.endedAt || null,
      domains: formData.domains
        .split(',')
        .map((d: string) => d.trim())
        .filter(Boolean),
      tags: formData.tags
        .split(',')
        .map((t: string) => t.trim())
        .filter(Boolean),
      projectId: formData.projectId,
      mentorLogins: formData.mentorLogins
        .split(',')
        .map((login: string) => login.trim())
        .filter(Boolean),
    }

    try {
      await updateModule({ variables: { input } })
      router.push(`/mentorship/programs`)
    } catch (err) {
      handleAppError(err)
    }
  }

  if (sessionStatus === 'loading' || queryLoading || !checkedAccess || !hasAccess || !formData) {
    return <LoadingSpinner />
  }

  return (
    <ModuleForm
      title="Edit Module"
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={mutationLoading}
      submitText="Update Module"
      isEdit
    />
  )
}

export default EditModulePage
