'use client'

import { useMutation, useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'
import { CREATE_MODULE } from 'server/queries/moduleQueries'
import { GET_PROGRAM_ADMIN_DETAILS } from 'server/queries/programsQueries'
import { SessionWithRole } from 'types/program'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/mainmoduleCard'

const CreateModulePage = () => {
  const router = useRouter()
  const { programKey } = useParams()
  const { data: sessionData, status: sessionStatus } = useSession()

  const [createModule, { loading }] = useMutation(CREATE_MODULE)
  const { data, loading: queryLoading } = useQuery(GET_PROGRAM_ADMIN_DETAILS, {
    variables: { programKey },
    skip: !programKey,
  })

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    experienceLevel: 'BEGINNER',
    startedAt: '',
    endedAt: '',
    domains: '',
    tags: '',
    projectId: '',
    mentorLogins: '',
  })

  const currentUserLogin = (sessionData as SessionWithRole)?.user?.username || ''

  const [checkedAccess, setCheckedAccess] = useState(false)
  const [hasAccess, setHasAccess] = useState(false)

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) return

    const programAdmins = data?.program?.admins || []
    const isAdmin = programAdmins.some(
      (admin: { name: string; login: string }) => admin.login === currentUserLogin
    )

    setHasAccess(isAdmin)
    setCheckedAccess(true)

    if (!isAdmin) {
      addToast({
        title: 'Access Denied',
        description: 'Only program admins can create modules.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.replace(`/mentorship/programs/${programKey}`)
    }
  }, [sessionStatus, queryLoading, data, currentUserLogin, router, programKey])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        name: formData.name,
        description: formData.description,
        experienceLevel: formData.experienceLevel,
        startedAt: formData.startedAt || null,
        endedAt: formData.endedAt || null,
        domains: formData.domains
          .split(',')
          .map((d) => d.trim())
          .filter(Boolean),
        tags: formData.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        programKey: programKey,
        projectId: formData.projectId,
        mentorLogins: formData.mentorLogins
          .split(',')
          .map((login) => login.trim())
          .filter(Boolean),
      }

      await createModule({ variables: { input } })
      router.push(`/mentorship/programs/${programKey}`)
    } catch (err) {
      addToast({
        title: 'Creation Failed',
        description: err.message || 'Something went wrong while creating the module.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
    }
  }

  if (sessionStatus === 'loading' || queryLoading || !checkedAccess || !hasAccess) {
    return <LoadingSpinner />
  }

  return (
    <ModuleForm
      title="Create New Module"
      submitText="Create Module"
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      isEdit={false}
    />
  )
}

export default CreateModulePage
