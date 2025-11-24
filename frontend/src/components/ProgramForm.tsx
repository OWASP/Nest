'use client'

import type React from 'react'
import DomainSelect from './DomainSelect'

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
  errors?: Partial<Record<keyof ProgramFormProps['formData'], string>>
}

const ProgramForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
  errors = {},
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
            <section className="flex flex-col gap-6">

              <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
                <div className="lg:col-span-2">
                  <label htmlFor="program-name" className="mb-2 block text-sm font-semibold">
                    Program Name *
                  </label>
                  <input
                    id="program-name"
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full rounded-lg border border-gray-600 bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]"
                  />
                </div>

                <div className="lg:col-span-2">
                  <label htmlFor="program-description" className="mb-2 block text-sm font-semibold">
                    Description *
                  </label>
                  <textarea
                    id="program-description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={4}
                    required
                    className="w-full rounded-lg border border-gray-600 bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]"
                  />
                </div>
              </div>
            </section>

            <section className="flex flex-col gap-6 text-gray-600 dark:text-gray-300">

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                <div>
                  <label htmlFor="program-start-date" className="mb-2 block text-sm font-semibold">
                    Start Date *
                  </label>
                  <input
                    id="program-start-date"
                    type="date"
                    name="startedAt"
                    value={formData.startedAt}
                    onChange={handleInputChange}
                    required
                    className={`w-full rounded-lg border ${errors.startedAt ? 'border-red-500' : 'border-gray-600'} bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]`}
                  />
                  {errors.startedAt && <p className="mt-1 text-sm text-red-500">{errors.startedAt}</p>}
                </div>
                <div>
                  <label htmlFor="program-end-date" className="mb-2 block text-sm font-semibold">
                    End Date *
                  </label>
                  <input
                    id="program-end-date"
                    type="date"
                    name="endedAt"
                    value={formData.endedAt}
                    onChange={handleInputChange}
                    required
                    className={`w-full rounded-lg border ${errors.endedAt ? 'border-red-500' : 'border-gray-600'} bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]`}
                  />
                  {errors.endedAt && <p className="mt-1 text-sm text-red-500">{errors.endedAt}</p>}
                </div>
                <div>
                  <label htmlFor="mentees-limit" className="mb-2 block text-sm font-semibold">
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
                    className={`w-full rounded-lg border ${errors.menteesLimit ? 'border-red-500' : 'border-gray-600'} bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]`}
                  />
                  {errors.menteesLimit && <p className="mt-1 text-sm text-red-500">{errors.menteesLimit}</p>}
                </div>
              </div>
            </section>

            <section className="flex flex-col gap-6">

              <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
                <div>
                  <label htmlFor="program-tags" className="mb-2 block text-sm font-semibold">
                    Tags
                  </label>
                  <input
                    id="program-tags"
                    type="text"
                    name="tags"
                    value={formData.tags}
                    onChange={handleInputChange}
                    placeholder="javascript, react"
                    className={`w-full rounded-lg border ${errors.tags ? 'border-red-500' : 'border-gray-600'} bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]`}
                  />
                  {errors.tags && <p className="mt-1 text-sm text-red-500">{errors.tags}</p>}
                </div>
                <div className="">
                  <DomainSelect
                    value={formData.domains}
                    onChange={(val) => setFormData((prev) => ({ ...prev, domains: val }))}
                    error={errors.domains}
                  />
                </div>
                {isEdit && (
                  <div className="lg:col-span-2">
                    <label
                      htmlFor="admin-github-usernames"
                      className="mb-2 block text-sm font-semibold"
                    >
                      Admin GitHub Usernames
                    </label>
                    <input
                      id="admin-github-usernames"
                      type="text"
                      name="adminLogins"
                      value={formData.adminLogins}
                      onChange={handleInputChange}
                      placeholder="johndoe, jane-doe"
                      className="w-full rounded-lg border border-gray-600 bg-gray-50 px-4 py-3 text-gray-800 focus:border-[#1D7BD7] focus:outline-none focus-visible:ring-1 focus-visible:ring-[#1D7BD7] dark:bg-gray-800 dark:text-gray-200 dark:focus-visible:ring-[#1D7BD7]"
                    />
                  </div>
                )}
              </div>
            </section>

            <div className="border-t border-gray-200 pt-8 text-gray-600 dark:border-gray-700 dark:text-gray-300">
              <div className="flex flex-col justify-end gap-4 sm:flex-row">
                <button
                  type="button"
                  onClick={() => history.back()}
                  className="rounded-lg border border-gray-50 px-6 py-3 font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
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
