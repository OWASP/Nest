'use client'

import { useMutation } from '@apollo/client'
import type React from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useState } from 'react'
import { CREATE_MODULE } from 'server/queries/moduleQueries'

const CreateModulePage = () => {
  const router = useRouter()
  const { programId } = useParams()

  const [createModule, { loading }] = useMutation(CREATE_MODULE)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    experienceLevel: 'BEGINNER',
    startedAt: '',
    endedAt: '',
    domains: '',
    tags: '',
    projectId: '',
    mentorLogins: '',
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const input = {
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
        programId: programId as string,
        projectId: formData.projectId,
        mentorLogins: formData.mentorLogins
          .split(',')
          .map((login) => login.trim())
          .filter(Boolean),
      }

      await createModule({ variables: { input } })
      //   toast.success('Module created!')
      router.push(`/mentorship/programs/${programId}`)
    } catch (err: any) {
      //   toast.error(err.message || 'Failed to create module')
    }
  }

  return (
    <div className="mx-auto mt-10 max-w-3xl rounded-2xl bg-white p-8 text-gray-600 shadow-lg dark:bg-[#212529] dark:text-gray-300">
      <h2 className="mb-6 text-2xl font-bold">Create New Module</h2>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="mb-1 block">Module Name</label>
          <input
            type="text"
            name="name"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            value={formData.name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label className="mb-1 block">Description</label>
          <textarea
            name="description"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            rows={4}
            value={formData.description}
            onChange={handleChange}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block">Experience Level</label>
            <select
              name="experienceLevel"
              value={formData.experienceLevel}
              onChange={handleChange}
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            >
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block">Mentor GitHub Logins (comma separated)</label>
            <input
              type="text"
              name="mentorLogins"
              value={formData.mentorLogins}
              onChange={handleChange}
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
              placeholder="e.g. johndoe, janedoe"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block">Start Date</label>
            <input
              type="datetime-local"
              name="startedAt"
              value={formData.startedAt}
              onChange={handleChange}
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            />
          </div>
          <div>
            <label className="mb-1 block">End Date</label>
            <input
              type="datetime-local"
              name="endedAt"
              value={formData.endedAt}
              onChange={handleChange}
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            />
          </div>
        </div>

        <div>
          <label className="mb-1 block">Domains (comma separated)</label>
          <input
            type="text"
            name="domains"
            value={formData.domains}
            onChange={handleChange}
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
          />
        </div>

        <div>
          <label className="mb-1 block">Tags (comma separated)</label>
          <input
            type="text"
            name="tags"
            value={formData.tags}
            onChange={handleChange}
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
          />
        </div>

        <div>
          <label className="mb-1 block">Project ID</label>
          <input
            type="text"
            name="projectId"
            value={formData.projectId}
            onChange={handleChange}
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            placeholder="Project UUID"
            required
          />
        </div>

        <button
          type="submit"
          className="mt-6 rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Creating...' : 'Create Module'}
        </button>
      </form>
    </div>
  )
}

export default CreateModulePage
