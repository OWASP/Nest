'use client'
import { useMutation } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useSession } from 'next-auth/react'
import React, { useEffect, useState } from 'react'

import { CreateProgramDocument } from 'types/__generated__/programsMutations.generated'
import { ExtendedSession } from 'types/auth'
import { parseCommaSeparated } from 'utils/parser'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/ProgramForm'

const CreateProgramPage = () => {
  const router = useRouter()
  const { data: session, status } = useSession()
  const isProjectLeader = (session as ExtendedSession)?.user.isLeader

  const [redirected, setRedirected] = useState(false)

  const [createProgram, { loading }] = useMutation(CreateProgramDocument)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    menteesLimit: 5,
    startedAt: '',
    endedAt: '',
    tags: '',
    domains: '',
  })

  useEffect(() => {
    if (status === 'loading') return

    if (!session || !isProjectLeader) {
      addToast({
        title: 'Access Denied',
        description: 'You must be project leader to create a program.',
        color: 'danger',
        variant: 'solid',
        timeout: 3000,
        shouldShowTimeoutProgress: true,
      })
      router.push('/')
      setRedirected(true)
    }
  }, [session, status, router, isProjectLeader])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
        name: formData.name,
        description: formData.description,
        menteesLimit: Number(formData.menteesLimit),
        startedAt: formData.startedAt,
        endedAt: formData.endedAt,
        tags: parseCommaSeparated(formData.tags),
        domains: parseCommaSeparated(formData.domains),
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

      router.push('/my/mentorship')
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

  if (status === 'loading' || !session || redirected) {
    return <LoadingSpinner />
  }

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
