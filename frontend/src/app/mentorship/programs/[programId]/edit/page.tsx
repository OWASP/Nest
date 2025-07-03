'use client'

import { useQuery, useMutation } from '@apollo/client'
import {
  faCalendarAlt,
  faInfoCircle,
  faPieChart,
  faPlus,
  faSave,
  faSpinner,
  faTags,
  faTimes,
  faUsers,
  faUserShield,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useEffect, useState } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_PROGRAM_DETAILS, UPDATE_PROGRAM } from 'server/queries/getProgramsQueries'
import { Contributor } from 'types/contributor'
import LoadingSpinner from 'components/LoadingSpinner'

const experienceOptions = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT']
const statusOptions = ['DRAFT', 'ACTIVE', 'COMPLETED']

const EditProgramPage = () => {
  const { data: sessionData } = useSession()
  const { programId } = useParams() as { programId: string }
  const [program, setProgram] = useState<any | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const { data, error } = useQuery(GET_PROGRAM_DETAILS, {
    variables: { id: programId },
  })

  const [updateProgram] = useMutation(UPDATE_PROGRAM)

  useEffect(() => {
    if (data?.program) {
      const p = data.program
      setProgram({
        ...p,
        experienceLevels: (p.experienceLevels ?? []).map((v: string) =>
          v.includes('.') ? v.split('.').pop()?.toUpperCase() : v.toUpperCase()
        ),
        status: p.status.includes('.')
          ? p.status.split('.').pop()?.toUpperCase()
          : p.status.toUpperCase(),
      })
    } else if (error) {
      handleAppError(error)
    }
  }, [data, error])

  const handleChange = (field: string, value: any) => {
    setProgram((prev: any) => ({ ...prev, [field]: value }))
  }

  const handleArrayChange = (field: string, index: number, value: string) => {
    const updated = [...program[field]]
    updated[index] = value
    handleChange(field, updated)
  }

  const handleArrayAdd = (field: string) => {
    handleChange(field, [...program[field], ''])
  }

  const handleArrayRemove = (field: string, index: number) => {
    const updated = [...program[field]]
    updated.splice(index, 1)
    handleChange(field, updated)
  }

  const handleExperienceToggle = (level: string) => {
    const updated = program.experienceLevels.includes(level)
      ? program.experienceLevels.filter((l: string) => l !== level)
      : [...program.experienceLevels, level]
    handleChange('experienceLevels', updated)
  }

  const handleSave = async () => {
    if (!program) return
    setIsSaving(true)

    try {
      await updateProgram({
        variables: {
          input: {
            id: program.id,
            name: program.name,
            description: program.description,
            status: program.status.toLowerCase(),
            startedAt: program.startedAt,
            endedAt: program.endedAt,
            menteesLimit: Number(program.menteesLimit),
            experienceLevels: program.experienceLevels.map((level: string) => level.toLowerCase()),
            tags: program.tags,
            domains: program.domains,
            adminLogins: program.admins.map((a: any) => a.login),
          },
        },
      })
    } catch (err) {
      handleAppError(err)
    } finally {
      setIsSaving(false)
    }
  }

  if (!program) return <LoadingSpinner />

  if (
    !program.admins.some(
      (admin: Contributor) =>
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        admin.login === (sessionData?.user as any)?.username
    )
  ) {
    return (
      <div className="flex min-h-screen items-center justify-center text-xl font-semibold text-red-600 dark:text-red-400">
        You don't have access to this content.
      </div>
    )
  }
  return (
    <div className="min-h-screen p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
      <div className="mx-auto max-w-4xl space-y-10">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Edit Program</h1>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 rounded-md border border-[#0D6EFD] px-4 py-2 text-[#0D6EFD] hover:bg-[#0D6EFD] hover:text-white dark:border-sky-600 dark:hover:bg-sky-600 dark:hover:text-white"
          >
            <FontAwesomeIcon icon={faSave} />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>

        {/* Basic Info */}
        <div className="space-y-6">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <FontAwesomeIcon icon={faInfoCircle} /> Basic Information
          </h2>

          <input
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
            placeholder="Program Name"
            value={program.name}
            onChange={(e) => handleChange('name', e.target.value)}
          />

          <textarea
            rows={4}
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
            placeholder="Program Description"
            value={program.description}
            onChange={(e) => handleChange('description', e.target.value)}
          />

          <select
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
            value={program.status}
            onChange={(e) => handleChange('status', e.target.value)}
          >
            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {/* Schedule */}
        <div className="space-y-6">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <FontAwesomeIcon icon={faCalendarAlt} /> Schedule
          </h2>

          <input
            type="date"
            value={program.startedAt}
            onChange={(e) => handleChange('startedAt', e.target.value)}
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
          />

          <input
            type="date"
            value={program.endedAt}
            onChange={(e) => handleChange('endedAt', e.target.value)}
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
          />
        </div>

        {/* Participants */}
        <div className="space-y-6">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <FontAwesomeIcon icon={faUsers} /> Participants
          </h2>

          <input
            type="number"
            value={program.menteesLimit || ''}
            onChange={(e) => handleChange('menteesLimit', e.target.value)}
            className="w-full rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
            placeholder="Mentees Limit"
          />

          <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
            {experienceOptions.map((level) => (
              <button
                key={level}
                onClick={() => handleExperienceToggle(level)}
                className={`rounded border-2 px-4 py-2 font-medium capitalize ${
                  program.experienceLevels.includes(level)
                    ? 'border-sky-500 bg-sky-100 dark:bg-sky-900 dark:text-sky-200'
                    : 'border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-300'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        {/* Tags and Domains */}
        {['tags', 'domains'].map((field) => (
          <div key={field} className="space-y-4">
            <h2 className="flex items-center gap-2 text-xl font-semibold">
              <FontAwesomeIcon icon={field === 'tags' ? faTags : faPieChart} />
              {field.charAt(0).toUpperCase() + field.slice(1)}
            </h2>

            {program[field].map((item: string, idx: number) => (
              <div key={idx} className="flex gap-3">
                <input
                  value={item}
                  onChange={(e) => handleArrayChange(field, idx, e.target.value)}
                  className="flex-1 rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
                  placeholder={`Enter ${field.slice(0, -1)}`}
                />
                <button
                  onClick={() => handleArrayRemove(field, idx)}
                  className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900"
                >
                  <FontAwesomeIcon icon={faTimes} />
                </button>
              </div>
            ))}

            <button
              onClick={() => handleArrayAdd(field)}
              className="flex items-center gap-2 font-medium text-sky-600"
            >
              <FontAwesomeIcon icon={faPlus} /> Add {field.slice(0, -1)}
            </button>
          </div>
        ))}

        {/* Admins */}
        <div className="space-y-6">
          <h2 className="flex items-center gap-2 text-xl font-semibold">
            <FontAwesomeIcon icon={faUserShield} /> Administrators
          </h2>

          {program.admins.map((admin: any, idx: number) => (
            <div key={idx} className="flex gap-3">
              <input
                value={admin.login}
                onChange={(e) =>
                  handleChange('admins', [
                    ...program.admins.slice(0, idx),
                    { login: e.target.value },
                    ...program.admins.slice(idx + 1),
                  ])
                }
                className="flex-1 rounded border px-4 py-2 dark:border-gray-600 dark:bg-gray-800"
                placeholder="GitHub username"
              />
              <button
                onClick={() =>
                  handleChange(
                    'admins',
                    program.admins.filter((_, i) => i !== idx)
                  )
                }
                className="px-3 py-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900"
              >
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </div>
          ))}

          <button
            onClick={() => handleChange('admins', [...program.admins, { login: '' }])}
            className="flex items-center gap-2 font-medium text-sky-600 hover:text-sky-700"
          >
            <FontAwesomeIcon icon={faPlus} />
            Add Administrator
          </button>
        </div>
      </div>

      {isSaving && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="flex items-center gap-4 rounded bg-white p-6 dark:bg-gray-800">
            <FontAwesomeIcon icon={faSpinner} spin className="text-sky-600" />
            <span className="font-medium">Saving changes...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default EditProgramPage
