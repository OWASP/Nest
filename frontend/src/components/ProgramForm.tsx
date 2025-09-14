'use client'

import type React from 'react'

interface ProgramFormProps {
  formData: {
    name: string
    description: string
    menteesLimit: number
    startedAt: string
    endedAt: string
    tags: string
    domains: string
    adminLogins?: string
    status?: string
  }
  setFormData: React.Dispatch<
    React.SetStateAction<{
      name: string
      description: string
      menteesLimit: number
      startedAt: string
      endedAt: string
      tags: string
      domains: string
      adminLogins?: string
      status?: string
    }>
  >
  onSubmit: (e: React.FormEvent) => void
  loading: boolean
  title: string
  submitText?: string
  isEdit?: boolean
}

const ProgramForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
}: ProgramFormProps) => {
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="text-text flex min-h-screen w-full flex-col items-center justify-normal p-5">
      <div className="mb-8 text-left">
        <h1 className="mb-2 text-4xl font-bold text-gray-800 dark:text-gray-200">{title}</h1>
      </div>

      <div className="overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-[#212529]">
        <form onSubmit={onSubmit}>
          <div className="flex flex-col gap-8 p-8">
            {/* Basic Information */}
            <section className="flex flex-col gap-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Basic Information
              </h2>
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div className="lg:col-span-2">
                  <label htmlFor="program-name" className="mb-2 block text-sm font-medium">
                    Program Name *
                  </label>
                  <input
                    id="program-name"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>

                <div className="lg:col-span-2">
                  <label htmlFor="program-description" className="mb-2 block text-sm font-medium">
                    Description *
                  </label>
                  <textarea
                    id="program-description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={4}
                    required
                    className="w-full resize-none rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
              </div>
            </section>

            {/* Configuration */}
            <section className="flex flex-col gap-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Program Configuration
              </h2>
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                <div>
                  <label htmlFor="program-start-date" className="mb-2 block text-sm font-medium">
                    Start Date *
                  </label>
                  <input
                    id="program-start-date"
                    type="date"
                    name="startedAt"
                    value={formData.startedAt}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="program-end-date" className="mb-2 block text-sm font-medium">
                    End Date *
                  </label>
                  <input
                    id="program-end-date"
                    type="date"
                    name="endedAt"
                    value={formData.endedAt}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="mentees-limit" className="mb-2 block text-sm font-medium">
                    Mentees Limit *
                  </label>
                  <input
                    id="mentees-limit"
                    type="number"
                    name="menteesLimit"
                    value={formData.menteesLimit}
                    onChange={handleInputChange}
                    min={1}
                    required
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
              </div>
            </section>

            {/* Additional Details */}
            <section className="flex flex-col gap-6">
              <h2 className="mb-6 text-2xl font-semibold text-gray-600 dark:text-gray-300">
                Additional Details
              </h2>
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <div>
                  <label htmlFor="program-tags" className="mb-2 block text-sm font-medium">
                    Tags
                  </label>
                  <input
                    id="program-tags"
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="javascript, react"
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                <div>
                  <label htmlFor="program-domains" className="mb-2 block text-sm font-medium">
                    Domains
                  </label>
                  <input
                    id="program-domains"
                    type="text"
                    name="domains"
                    value={formData.domains}
                    onChange={handleInputChange}
                    placeholder="AI, Web Development"
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                  />
                </div>
                {isEdit && (
                  <div className="lg:col-span-2">
                    <label
                      htmlFor="mentor-github-usernames"
                      className="mb-2 block text-sm font-medium"
                    >
                      Admin GitHub Usernames
                    </label>
                    <input
                      id="mentor-github-usernames"
                      type="text"
                      name="adminLogins"
                      value={formData.adminLogins}
                      onChange={handleInputChange}
                      placeholder="johndoe, jane-doe"
                      className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200"
                    />
                  </div>
                )}
              </div>
            </section>

            {/* Submit Buttons */}
            <div className="border-t-1 border-t-gray-200 pt-8 dark:border-t-gray-700">
              <div className="flex flex-col justify-end gap-4 sm:flex-row">
                <button
                  type="button"
                  onClick={() => history.back()}
                  className="rounded-lg border-1 border-gray-200 px-6 py-3 font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center justify-center gap-2 rounded-md border border-[#1D7BD7] bg-transparent px-6 py-2 whitespace-nowrap text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white"
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

export default ProgramForm
