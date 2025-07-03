'use client'

import { useMutation } from '@apollo/client'
import { useToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { CREATE_PROGRAM } from 'server/queries/getProgramsQueries'

const CreateProgramPage = () => {
  const router = useRouter()
  const [createProgram, { loading }] = useMutation(CREATE_PROGRAM)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    menteesLimit: 5,
    startedAt: '',
    endedAt: '',
    experienceLevels: '',
    tags: '',
    domains: '',
    adminLogins: '',
    status: 'DRAFT',
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
        menteesLimit: Number(formData.menteesLimit),
        startedAt: formData.startedAt,
        endedAt: formData.endedAt,
        experienceLevels: formData.experienceLevels
          .split(',')
          .map((e) => e.trim())
          .filter(Boolean),
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
        status: formData.status, // enum should match backend e.g. "draft"
      }

      await createProgram({ variables: { input } })
      //   toast.success('Program created successfully!')
      router.push('/mentorship/programs')
    } catch (err: any) {
      //   toast.error(err.message || 'Failed to create program')
    }
  }

  return (
    <div className="mx-auto mt-10 max-w-3xl rounded-2xl bg-white p-8 text-gray-600 shadow-lg dark:bg-[#212529] dark:text-gray-300">
      <h2 className="mb-6 text-2xl font-bold">Create New Program</h2>
      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="mb-1 block">Program Name</label>
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
            value={formData.description}
            onChange={handleChange}
            rows={4}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block">Start Date</label>
            <input
              type="datetime-local"
              name="startedAt"
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
              value={formData.startedAt}
              onChange={handleChange}
              required
            />
          </div>
          <div>
            <label className="mb-1 block">End Date</label>
            <input
              type="datetime-local"
              name="endedAt"
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
              value={formData.endedAt}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="mb-1 block">Mentees Limit</label>
            <input
              type="number"
              name="menteesLimit"
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
              value={formData.menteesLimit}
              onChange={handleChange}
              required
              min={1}
            />
          </div>
          <div>
            <label className="mb-1 block">Status</label>
            <select
              name="status"
              className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="DRAFT">Draft</option>
              <option value="ACTIVE">Active</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>
        </div>

        <div>
          <label className="mb-1 block">Experience Levels (comma separated)</label>
          <input
            type="text"
            name="experienceLevels"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            value={formData.experienceLevels}
            onChange={handleChange}
          />
        </div>

        <div>
          <label className="mb-1 block">Tags (comma separated)</label>
          <input
            type="text"
            name="tags"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            value={formData.tags}
            onChange={handleChange}
          />
        </div>

        <div>
          <label className="mb-1 block">Domains (comma separated)</label>
          <input
            type="text"
            name="domains"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            value={formData.domains}
            onChange={handleChange}
          />
        </div>

        <div>
          <label className="mb-1 block">Mentor GitHub Usernames (comma separated)</label>
          <input
            type="text"
            name="adminLogins"
            className="w-full rounded border border-zinc-700 bg-gray-100 p-2 dark:bg-zinc-800"
            value={formData.adminLogins}
            onChange={handleChange}
            placeholder="e.g. johndoe, janedoe"
          />
        </div>

        <button
          type="submit"
          className="mt-4 rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? 'Creating...' : 'Create Program'}
        </button>
      </form>
    </div>
  )
}

export default CreateProgramPage
