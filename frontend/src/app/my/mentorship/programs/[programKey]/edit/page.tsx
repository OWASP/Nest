'use client'
import { useMutation, useQuery } from '@apollo/client/react'
import { addToast } from '@heroui/toast'
import { useRouter, useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import type React from 'react'
import { useState, useEffect } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { UpdateProgramDocument } from 'types/__generated__/programsMutations.generated'
import { GetProgramDetailsDocument } from 'types/__generated__/programsQueries.generated'
import type { ExtendedSession } from 'types/auth'
import { formatDateForInput } from 'utils/dateFormatter'
import { parseCommaSeparated } from 'utils/parser'
import slugify from 'utils/slugify'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/ProgramForm'
const EditProgramPage = () => {
  const router = useRouter()
  const { programKey } = useParams<{ programKey: string }>()
  const { data: session, status: sessionStatus } = useSession()
  const [updateProgram, { loading: mutationLoading }] = useMutation(UpdateProgramDocument)
  const {
    data,
    error,
    loading: queryLoading,
  } = useQuery(GetProgramDetailsDocument, {
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
    tags: '',
    domains: '',
    adminLogins: '',
    status: ProgramStatusEnum.Draft,
  })
  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')
  useEffect(() => {
    if (sessionStatus === 'loading' || queryLoading) {
      return
    }
    if (!data?.getProgram || sessionStatus === 'unauthenticated') {
      setAccessStatus('denied')
      return
    }

    const isAdmin = data.getProgram.admins?.some(
      (admin: { login: string }) => admin.login === (session as ExtendedSession)?.user?.login
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
      setTimeout(() => router.replace('/my/mentorship/programs'), 1500)
    }
  }, [sessionStatus, session, data, queryLoading, router])
  useEffect(() => {
    if (accessStatus === 'allowed' && data?.getProgram) {
      const { getProgram: program } = data
      setFormData({
        name: program.name || '',
        description: program.description || '',
        menteesLimit: program.menteesLimit ?? 5,
        startedAt: formatDateForInput(program.startedAt),
        endedAt: formatDateForInput(program.endedAt),
        tags: (program.tags || []).join(', '),
        domains: (program.domains || []).join(', '),
        adminLogins: (program.admins || [])
          .map((admin: { login: string }) => admin.login)
          .join(', '),
        status: program.status || ProgramStatusEnum.Draft,
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
        tags: parseCommaSeparated(formData.tags),
        domains: parseCommaSeparated(formData.domains),
        adminLogins: parseCommaSeparated(formData.adminLogins),
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

      router.push(`/my/mentorship/programs/${slugify(formData.name)}`)
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
      submitText="Save"
      isEdit={true}
    />
  )
}
export default EditProgramPage
