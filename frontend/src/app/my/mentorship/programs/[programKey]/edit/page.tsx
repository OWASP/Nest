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
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'
import type { ExtendedSession } from 'types/auth'
import { formatDateForInput } from 'utils/dateFormatter'
import { parseCommaSeparated } from 'utils/parser'
import slugify from 'utils/slugify'
import { validateTags } from 'utils/validators'
import LoadingSpinner from 'components/LoadingSpinner'
import ProgramForm from 'components/ProgramForm'
import { useForm } from 'hooks/useForm'
const EditProgramPage = () => {
  const router = useRouter()
  const { programKey } = useParams<{ programKey: string }>()
  const { data: session, status: sessionStatus } = useSession()
  const [updateProgram, { loading: mutationLoading }] = useMutation(UpdateProgramDocument)
  const {
    data,
    error,
    loading: queryLoading,
  } = useQuery(GetProgramAndModulesDocument, {
    variables: { programKey },
    skip: !programKey,
    fetchPolicy: 'network-only',
  })

  const [accessStatus, setAccessStatus] = useState<'checking' | 'allowed' | 'denied'>('checking')

  const validate = (values: any) => {
    const errors: Record<string, string> = {}

    if (!values.name) errors.name = 'Name is required'
    if (!values.description) errors.description = 'Description is required'
    if (!values.startedAt) errors.startedAt = 'Start date is required'
    if (!values.endedAt) errors.endedAt = 'End date is required'

    if (values.startedAt && values.endedAt) {
      if (new Date(values.startedAt) > new Date(values.endedAt)) {
        errors.startedAt = 'Start date cannot be after end date'
      }
    }

    if (data?.getProgramModules) {
      const programStart = new Date(values.startedAt).getTime()
      const programEnd = new Date(values.endedAt).getTime()

      for (const module of data.getProgramModules) {
        const moduleStart = new Date(module.startedAt).getTime()
        const moduleEnd = new Date(module.endedAt).getTime()

        if (moduleStart < programStart) {
          errors.startedAt = `Module "${module.name}" starts before the program.`
        }

        if (moduleEnd > programEnd) {
          errors.endedAt = `Module "${module.name}" ends after the program.`
        }
      }
    }

    const tagError = validateTags(values.tags)
    if (tagError) errors.tags = tagError

    return errors
  }

  const { values, errors, isSubmitting, handleSubmit, setValues, setErrors } = useForm({
    initialValues: {
      name: '',
      description: '',
      menteesLimit: 5,
      startedAt: '',
      endedAt: '',
      tags: '',
      domains: '',
      adminLogins: '',
      status: ProgramStatusEnum.Draft,
    },
    validate,
    onSubmit: async (values) => {
      try {
        const input = {
          key: programKey,
          name: values.name,
          description: values.description,
          menteesLimit: Number(values.menteesLimit),
          startedAt: values.startedAt,
          endedAt: values.endedAt,
          tags: parseCommaSeparated(values.tags),
          domains: parseCommaSeparated(values.domains),
          adminLogins: parseCommaSeparated(values.adminLogins),
          status: values.status as ProgramStatusEnum,
        }

        await updateProgram({ variables: { input } })

        addToast({
          title: 'Program Updated',
          description: 'The program has been successfully updated.',
          color: 'success',
          variant: 'solid',
          timeout: 3000,
        })

        router.push(`/my/mentorship/programs/${slugify(values.name)}`)
      } catch (err: any) {
        let errorMessage = 'There was an error updating the program.'
        if (err?.message?.toLowerCase().includes('duplicate') || err?.message?.toLowerCase().includes('unique')) {
          errorMessage = 'A program with this name already exists. Please choose a different name.'
          setErrors((prev) => ({ ...prev, name: errorMessage }))
        }

        addToast({
          title: 'Update Failed',
          description: errorMessage,
          color: 'danger',
          variant: 'solid',
          timeout: 3000,
        })
        if (errorMessage !== 'A program with this name already exists. Please choose a different name.') {
          handleAppError(err)
        }
      }
    },
  })

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
      setValues({
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
  }, [accessStatus, data, error, setValues])

  if (accessStatus === 'checking' || (queryLoading && !values.name)) {
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
      formData={values}
      setFormData={setValues}
      onSubmit={handleSubmit}
      loading={isSubmitting}
      title="Edit Program"
      submitText="Save"
      isEdit={true}
      errors={errors}
    />
  )
}
export default EditProgramPage
