'use client'

import { useMutation, useQuery } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'
import { ErrorDisplay } from 'app/global-error'
import { CREATE_MODULE } from 'server/queries/moduleQueries'
import { GET_PROGRAM_ADMIN_DETAILS } from 'server/queries/programsQueries'
import { ExtendedSession } from 'types/program'
import { parseCommaSeparated } from 'utils/parser'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/mainmoduleCard'

const CreateModulePage = () => {
  const router = useRouter()
  const { programKey } = useParams() as { programKey: string }
  const { data: sessionData, status: sessionStatus } = useSession()

  const [createModule, { loading: mutationLoading }] = useMutation(CREATE_MODULE)

  const {
    data: programData,
    loading: queryLoading,
    error: queryError,
  } = useQuery(GET_PROGRAM_ADMIN_DETAILS, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'network-only',
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
    projectName: '',
    mentorLogins: '',
  })

  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }

    if (queryError || !programData?.program || sessionStatus === 'unauthenticated') {
      setAccessStatus('denied')
      return
    }

    const currentUserLogin = (sessionData as ExtendedSession)?.user?.login
    const isAdmin = programData.program.admins?.some(
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
      setTimeout(() => router.replace('/mentorship/programs'), 1500)
    }
  }, [sessionStatus, sessionData, queryLoading, programData, programKey, queryError, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        name: formData.name,
        description: formData.description,
        experienceLevel: formData.experienceLevel,
        startedAt: formData.startedAt || null,
        endedAt: formData.endedAt || null,
        domains: parseCommaSeparated(formData.domains),
        tags: parseCommaSeparated(formData.tags),
        programKey: programKey,
        projectId: formData.projectId,
        projectName: formData.projectName,
        mentorLogins: parseCommaSeparated(formData.mentorLogins),
      }

      await createModule({ variables: { input } })

      addToast({
        title: 'Module Created',
        description: 'The new module has been successfully created.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })

      router.push(`/mentorship/programs`)
    } catch (err) {
      addToast({
        title: 'Creation Failed',
        description: err.message || 'Something went wrong while creating the module.',
        color: 'danger',
        variant: 'solid',
        timeout: 4000,
      })
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
    />
  )
}

export default CreateModulePage
