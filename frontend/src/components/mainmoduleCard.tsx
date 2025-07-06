'use client'

import type React from 'react'

interface ModuleFormProps {
  formData: {
    name: string
    description: string
    experienceLevel: string
    startedAt: string
    endedAt: string
    domains: string
    tags: string
    projectId: string
    mentorLogins: string
  }
  setFormData: React.Dispatch<React.SetStateAction<ModuleFormProps['formData']>>
  onSubmit: (e: React.FormEvent) => void
  loading: boolean
  isEdit?: boolean
  title: string
  submitText?: string
}

const EXPERIENCE_LEVELS = [
  { key: 'BEGINNER', label: 'Beginner' },
  { key: 'INTERMEDIATE', label: 'Intermediate' },
  { key: 'ADVANCED', label: 'Advanced' },
  { key: 'EXPERT', label: 'Expert' },
]

const ModuleForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
}: ModuleFormProps) => {
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="flex w-full flex-col items-center justify-normal p-5 text-text">
      <div className="mb-8 text-left">
        <h1 className="mb-2 text-4xl font-bold text-gray-800 dark:text-gray-200">{title}</h1>
      </div>

      <div className="overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-[#212529]">
        <form onSubmit={onSubmit}>
          <div className="space-y-8 p-8">
            <section className="space-y-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Module Information
              </h2>
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="lg:col-span-2">
                  <label htmlFor="module-name" className="mb-2 block text-sm font-medium">
                    Module Name *
                  </label>
                  <input
                    id="module-name"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>

                <div className="lg:col-span-2">
                  <label htmlFor="module-description" className="mb-2 block text-sm font-medium">
                    Description *
                  </label>
                  <textarea
                    id="module-description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={4}
                    required
                    className="w-full resize-none rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Module Configuration
              </h2>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                <div>
                  <label htmlFor="startedAt" className="mb-2 block text-sm font-medium">
                    Start Date *
                  </label>
                  <input
                    type="date"
                    name="startedAt"
                    id="startedAt"
                    value={formData.startedAt}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="endedAt" className="mb-2 block text-sm font-medium">
                    End Date *
                  </label>
                  <input
                    type="date"
                    name="endedAt"
                    id="endedAt"
                    value={formData.endedAt}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="experienceLevel" className="mb-2 block text-sm font-medium">
                    Experience Level
                  </label>
                  <select
                    name="experienceLevel"
                    id="experienceLevel"
                    value={formData.experienceLevel}
                    onChange={handleInputChange}
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  >
                    {EXPERIENCE_LEVELS.map((lvl) => (
                      <option key={lvl.key} value={lvl.key}>
                        {lvl.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Additional Details
              </h2>
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div>
                  <label htmlFor="domains" className="mb-2 block text-sm font-medium">
                    Domains
                  </label>
                  <input
                    id="domains"
                    type="text"
                    name="domains"
                    value={formData.domains}
                    onChange={handleInputChange}
                    placeholder="AI, Web Development"
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="tags" className="mb-2 block text-sm font-medium">
                    Tags
                  </label>
                  <input
                    id="tags"
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="javascript, react"
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="projectId" className="mb-2 block text-sm font-medium">
                    Project ID
                  </label>
                  <input
                    id="projectId"
                    type="text"
                    name="projectId"
                    value={formData.projectId}
                    onChange={handleInputChange}
                    placeholder="Project UUID"
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                {isEdit && (
                  <div className="lg:col-span-2">
                    <label htmlFor="mentorLogins" className="mb-2 block text-sm font-medium">
                      Mentor GitHub Usernames
                    </label>
                    <input
                      id="mentorLogins"
                      type="text"
                      name="mentorLogins"
                      value={formData.mentorLogins}
                      onChange={handleInputChange}
                      placeholder="johndoe, janedoe"
                      className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-none dark:bg-gray-800 dark:text-gray-200"
                    />
                  </div>
                )}
              </div>
            </section>

            <div className="border-t pt-8">
              <div className="flex flex-col justify-end gap-4 sm:flex-row">
                <button
                  type="button"
                  onClick={() => history.back()}
                  className="rounded-lg border px-6 py-3 font-medium text-gray-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center justify-center gap-2 rounded-md border border-[#0D6EFD] px-4 py-2 text-[#0D6EFD] hover:bg-[#0D6EFD] hover:text-white dark:text-sky-600 dark:hover:bg-sky-100"
                >
                  {loading ? 'Saving...' : submitText}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ModuleForm
