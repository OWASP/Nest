'use client'

import { useQuery, useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import type React from 'react'
import { useState, useEffect } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROGRAM_DETAILS, UPDATE_PROGRAM } from 'server/queries/getProgramsQueries'
import { SessionWithRole } from 'types/program'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/programCard'

const EditProgramPage = () => {
  const router = useRouter()
  const { programId } = useParams() as { programId: string }
  const { data: session, status: sessionStatus } = useSession()
  const [updateProgram, { loading }] = useMutation(UPDATE_PROGRAM)

  const {
    data,
    error,
    loading: queryLoading,
  } = useQuery(GET_PROGRAM_DETAILS, {
    variables: { programId },
    skip: !programId,
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

  const [checkedAccess, setCheckedAccess] = useState(false)
  const [hasAccess, setHasAccess] = useState(false)

  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) return

    const isMentor = (session as SessionWithRole)?.user?.role === 'mentor'
    const isAdmin = data?.program?.admins?.some(
      (admin: { login: string }) => admin.login === (session as SessionWithRole)?.user?.username
    )

    if (!isMentor || !isAdmin) {
      addToast({
        title: 'Access Denied',
        description: 'Only mentors listed as program admins can edit this program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.replace('/mentorship/programs')
    } else {
      setHasAccess(true)
    }

    setCheckedAccess(true)
  }, [sessionStatus, session, data, queryLoading, router])

  useEffect(() => {
    if (data?.program) {
      const program = data.program

      const formatDateForInput = (dateStr: string) => {
        if (!dateStr) return ''
        const date = new Date(dateStr)
        return date.toISOString().slice(0, 10)
      }

      setFormData({
        name: program.name || '',
        description: program.description || '',
        menteesLimit: program.menteesLimit || 5,
        startedAt: formatDateForInput(program.startedAt),
        endedAt: formatDateForInput(program.endedAt),
        experienceLevels: (program.experienceLevels || []).map((lvl: string) =>
          lvl.includes('.') ? lvl.split('.').pop()?.toUpperCase() : lvl.toUpperCase()
        ),
        tags: (program.tags || []).join(', '),
        domains: (program.domains || []).join(', '),
        adminLogins: (program.admins || [])
          .map((admin: { login: string }) => admin.login)
          .join(', '),
        status: program.status.includes('.')
          ? program.status.split('.').pop()?.toUpperCase()
          : program.status.toUpperCase(),
      })
    } else if (error) {
      handleAppError(error)
    }
  }, [data, error])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        id: programId,
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
        shouldShowTimeoutProgress: true,
      })

      router.push('/mentorship/programs')
    } catch (err) {
      addToast({
        title: 'Update Failed',
        description: 'There was an error updating the program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      handleAppError(err)
    }
  }

  if (sessionStatus === 'loading' || queryLoading || !checkedAccess || !hasAccess) {
    return <LoadingSpinner />
  }

  return (
    <ProgramForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      title="Edit Program"
      submitText="Save Changes"
      isEdit={true}
    />
  )
}

export default EditProgramPage
