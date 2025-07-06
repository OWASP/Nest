'use client'

import { useQuery, useMutation } from '@apollo/client'
import { useParams, useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import type React from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROGRAM_ADMINS_AND_MODULES, UPDATE_MODULE } from 'server/queries/moduleQueries'
import LoadingSpinner from 'components/LoadingSpinner'
import ModuleForm from 'components/mainmoduleCard'

const EditModulePage = () => {
  const { programId, moduleId } = useParams()
  const router = useRouter()
  const [formData, setFormData] = useState<any>(null)
  const [updateModule, { loading }] = useMutation(UPDATE_MODULE)
  const { data, error } = useQuery(GET_PROGRAM_ADMINS_AND_MODULES, {
    variables: {
      programId,
      moduleId,
    },
  })

  const formatDateForInput = (dateStr: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toISOString().slice(0, 10)
  }

  useEffect(() => {
    if (data?.getModule) {
      const m = data.getModule
      setFormData({
        id: m.id,
        name: m.name,
        description: m.description,
        experienceLevel: m.experienceLevel || 'BEGINNER',
        startedAt: formatDateForInput(m.startedAt) || '',
        endedAt: formatDateForInput(m.endedAt) || '',
        domains: m.domains?.join(', ') || '',
        tags: m.tags?.join(', ') || '',
        projectId: m.projectId || '',
        mentorLogins: m.mentors?.map((m: any) => m.login).join(', ') || '',
      })
    } else if (error) {
      handleAppError(error)
    }
  }, [data, error])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData) return

    try {
      const input = {
        id: formData.id,
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
        projectId: formData.projectId,
        mentorLogins: formData.mentorLogins
          .split(',')
          .map((login) => login.trim())
          .filter(Boolean),
      }

      await updateModule({ variables: { input } })
      router.push(`/mentorship/programs`)
    } catch (err) {
      handleAppError(err)
    }
  }

  if (!formData) return <LoadingSpinner />

  return (
    <ModuleForm
      title="Edit Module"
      formData={formData}
      setFormData={setFormData}
      onSubmit={handleSubmit}
      loading={loading}
      submitText="Update Module"
      isEdit={true}
    />
  )
}

export default EditModulePage
