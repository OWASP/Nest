'use client'

import { useMutation } from '@apollo/client'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import type React from 'react'
import { useEffect, useState } from 'react'
import { CREATE_PROGRAM } from 'server/queries/programsQueries'
import { SessionWithRole } from 'types/program'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/programCard'

const CreateProgramPage = () => {
  const router = useRouter()
  const { data: session, status } = useSession()
  const [createProgram, { loading }] = useMutation(CREATE_PROGRAM)

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

  useEffect(() => {
    if (status === 'loading') return
    const userRole = (session as SessionWithRole)?.user?.role
    if (!session || userRole !== 'mentor') {
      addToast({
        title: 'Access Denied',
        description: 'You must be a mentor to create a program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.push('/mentorship/programs')
      return
    }
  }, [session, status, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
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

      await createProgram({ variables: { input } })

      addToast({
        description: 'Program created successfully!',
        title: 'Success',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'success',
        variant: 'solid',
      })

      router.push('/mentorship/programs')
    } catch (err) {
      addToast({
        description: err?.message || 'Unable to complete the requested operation.',
        title: 'GraphQL Request Failed',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
        color: 'danger',
        variant: 'solid',
      })
    }
  }

  if (status === 'loading' || !session) return <LoadingSpinner />

  return (
    <ProgramForm
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      title="Create Program"
      isEdit={false}
    />
  )
}

export default CreateProgramPage
