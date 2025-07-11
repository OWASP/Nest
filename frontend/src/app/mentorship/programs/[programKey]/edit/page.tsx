'use client'
import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import type React from 'react'
import { useState, useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GET_PROGRAM_DETAILS, UPDATE_PROGRAM } from 'server/queries/programsQueries'
import { SessionWithRole } from 'types/program'
import { formatDateForInput } from 'utils/dateFormatter'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/programCard'
const EditProgramPage = () => {
  const router = useRouter()
  const { programKey } = useParams() as { programKey: string }
  const { data: session, status: sessionStatus } = useSession()
  const [updateProgram, { loading: mutationLoading }] = useMutation(UPDATE_PROGRAM)
  const {
    data,
    error,
    loading: queryLoading,
  } = useQuery(GET_PROGRAM_DETAILS, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'network-only',
  })
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    menteesLimit: 5,
    startedAt: '',
    endedAt: '',
    experienceLevels: [] as string[],
    tags: '',
    domains: '',
    adminLogins: '',
    status: 'DRAFT',
  })
  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')
  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }
    if (!data?.program || sessionStatus === 'unauthenticated') {
      setAccessStatus('denied')
      return
    }

    const isAdmin = data.program.admins?.some(
      (admin: { login: string }) => admin.login === (session as SessionWithRole)?.user?.login
    )

    if (isAdmin) {
      setAccessStatus('allowed')
    } else {
      setAccessStatus('denied')
      addToast({
        title: 'Access Denied',
        description: 'Only program admins can edit this page.',
        color: 'danger',
        variant: 'solid',
        timeout: 4000,
      })
      setTimeout(() => router.replace('/mentorship/programs'), 1500)
    }
  }, [sessionStatus, session, data, queryLoading, router])
  useEffect(() => {
    if (accessStatus === 'allowed' && data?.program) {
      const { program } = data
      setFormData({
        name: program.name || '',
        description: program.description || '',
        menteesLimit: program.menteesLimit ?? 5,
        startedAt: formatDateForInput(program.startedAt),
        endedAt: formatDateForInput(program.endedAt),
        experienceLevels: program.experienceLevels || [],
        tags: (program.tags || []).join(', '),
        domains: (program.domains || []).join(', '),
        adminLogins: (program.admins || [])
          .map((admin: { login: string }) => admin.login)
          .join(', '),
        status: program.status || 'DRAFT',
      })
    } else if (error) {
      handleAppError(error)
    }
  }, [accessStatus, data, error])
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const input = {
        key: programKey,
        name: formData.name,
        description: formData.description,
        menteesLimit: Number(formData.menteesLimit),
        startedAt: formData.startedAt,
        endedAt: formData.endedAt,
        experienceLevels: formData.experienceLevels,
        tags: formData.tags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean),
        domains: formData.domains
          .split(',')
          .map((d) => d.trim())
          .filter(Boolean),
        adminLogins: formData.adminLogins
          .split(',')
          .map((login) => login.trim())
          .filter(Boolean),
        status: formData.status,
      }

      await updateProgram({ variables: { input } })

      addToast({
        title: 'Program Updated',
        description: 'The program has been successfully updated.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })

      router.push(`/mentorship/programs`)
    } catch (err) {
      addToast({
        title: 'Update Failed',
        description: 'There was an error updating the program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
      })
      handleAppError(err)
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
        message="You do not have permission to view this page. You will be redirected."
      />
    )
  }
  return (
    <ProgramForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={mutationLoading}
      title="Edit Program"
      submitText="Save Changes"
      isEdit={true}
    />
  )
}
export default EditProgramPage
