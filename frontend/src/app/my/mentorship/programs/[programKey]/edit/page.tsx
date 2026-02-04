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
import {
  GetMyProgramsDocument,
  GetProgramDetailsDocument,
} from 'types/__generated__/programsQueries.generated'
import { formatDateForInput } from 'utils/dateFormatter'
import { parseCommaSeparated } from 'utils/parser'
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
  const [formData, setFormData] = useState<{
    name: string
    description: string
    menteesLimit: number
    startedAt: string
    endedAt: string
    tags: string
    domains: string
    adminLogins?: string
    status?: string
  }>({
    name: '',
    description: '',
    menteesLimit: 0,
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

    const userLogin: string | undefined =
      session?.user && 'login' in session.user
        ? (session.user as { login?: string }).login
        : undefined

    const isAdmin = data.getProgram.admins?.some(
      (admin: { login: string }) => admin.login === userLogin
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
        menteesLimit: program.menteesLimit ?? 0,
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
        status: (formData.status as ProgramStatusEnum) || ProgramStatusEnum.Draft,
      }

      const result = await updateProgram({
        awaitRefetchQueries: true,
        refetchQueries: [{ query: GetMyProgramsDocument }],
        variables: { input },
      })
      const updatedProgramKey = result.data?.updateProgram?.key || programKey

      addToast({
        title: 'Program Updated',
        description: 'The program has been successfully updated.',
        color: 'success',
        variant: 'solid',
        timeout: 3000,
      })

      router.push(`/my/mentorship/programs/${updatedProgramKey}`)
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
      currentProgramKey={programKey}
    />
  )
}
export default EditProgramPage
