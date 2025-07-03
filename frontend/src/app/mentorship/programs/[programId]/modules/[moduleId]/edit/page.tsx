'use client'

import { useQuery, useMutation } from '@apollo/client'
import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import { handleAppError } from 'app/global-error'
import { GET_MODULE_BY_ID, UPDATE_MODULE } from 'server/queries/moduleQueries'
import LoadingSpinner from 'components/LoadingSpinner'

const EditModulePage = () => {
  const { moduleId } = useParams()
  const [module, setModule] = useState<any | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const { data, error } = useQuery(GET_MODULE_BY_ID, {
    variables: { id: moduleId },
  })

  const [updateModule] = useMutation(UPDATE_MODULE)

  useEffect(() => {
    if (data?.getModule) {
      setModule(data.getModule)
    } else if (error) {
      handleAppError(error)
    }
  }, [data, error])

  const handleChange = (field: string, value: any) => {
    setModule((prev: any) => ({ ...prev, [field]: value }))
  }

  const handleSave = async () => {
    if (!module) return
    setIsSaving(true)

    try {
      await updateModule({
        variables: {
          input: {
            id: module.id,
            name: module.name,
            description: module.description,
            experienceLevel: module.experienceLevel,
            startedAt: module.startedAt,
            endedAt: module.endedAt,
            domains: module.domains,
            tags: module.tags,
            projectId: module.projectId,
            mentorLogins: module.mentors.map((m: any) => m.login),
          },
        },
      })
    } catch (err) {
      handleAppError(err)
    } finally {
      setIsSaving(false)
    }
  }

  if (!module) return <LoadingSpinner />

  return (
    <div className="min-h-screen p-8 text-gray-200 dark:bg-[#212529]">
      <div className="mx-auto max-w-3xl space-y-6">
        <h1 className="mb-4 text-2xl font-bold">Edit Module</h1>

        <div>
          <label>Name</label>
          <input
            value={module.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>Description</label>
          <textarea
            value={module.description}
            onChange={(e) => handleChange('description', e.target.value)}
            rows={4}
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>Start Date</label>
          <input
            type="date"
            value={module.startedAt}
            onChange={(e) => handleChange('startedAt', e.target.value)}
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>End Date</label>
          <input
            type="date"
            value={module.endedAt}
            onChange={(e) => handleChange('endedAt', e.target.value)}
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>Tags (comma separated)</label>
          <input
            value={module.tags.join(', ')}
            onChange={(e) =>
              handleChange(
                'tags',
                e.target.value.split(',').map((t) => t.trim())
              )
            }
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>Domains (comma separated)</label>
          <input
            value={module.domains.join(', ')}
            onChange={(e) =>
              handleChange(
                'domains',
                e.target.value.split(',').map((t) => t.trim())
              )
            }
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <div>
          <label>Mentor GitHub Logins (comma separated)</label>
          <input
            value={module.mentors.map((m: any) => m.login).join(', ')}
            onChange={(e) =>
              handleChange(
                'mentors',
                e.target.value.split(',').map((login) => ({ githubUser: { login: login.trim() } }))
              )
            }
            className="w-full rounded border border-gray-600 bg-gray-800 p-2"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={isSaving}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          {isSaving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}

export default EditModulePage
