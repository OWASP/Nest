'use client'
import { useApolloClient } from '@apollo/client/react'
import clsx from 'clsx'
import debounce from 'lodash/debounce'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useEffect, useCallback, useRef } from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'

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
    projectName: string
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
  { key: ExperienceLevelEnum.Beginner, label: 'Beginner' },
  { key: ExperienceLevelEnum.Intermediate, label: 'Intermediate' },
  { key: ExperienceLevelEnum.Advanced, label: 'Advanced' },
  { key: ExperienceLevelEnum.Expert, label: 'Expert' },
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
  const router = useRouter()
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  return (
    <div className="text-text flex w-full flex-col items-center justify-normal p-5">
      <div className="mb-8 text-left">
        <h1 className="mb-2 text-4xl font-bold text-gray-800 dark:text-gray-200">{title}</h1>
      </div>

      <div className="overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-[#212529]">
        <form onSubmit={onSubmit}>
          <div className="flex flex-col gap-8 p-8">
            <section className="flex flex-col gap-6">
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
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
                    className="w-full resize-none rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
                  />
                </div>
              </div>
            </section>

            <section className="flex flex-col gap-6">
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
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

            <section className="flex flex-col gap-6">
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
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
                    className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
                  />
                </div>
                <div>
                  <ProjectSelector
                    value={formData.projectId}
                    defaultName={formData.projectName}
                    onProjectChange={(id, name) =>
                      setFormData((prev) => ({
                        ...prev,
                        projectId: id ?? '',
                        projectName: name,
                      }))
                    }
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
                      placeholder="johndoe, jane-doe"
                      className="w-full rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400"
                    />
                  </div>
                )}
              </div>
            </section>

            <div className="border-t border-t-gray-200 pt-8 dark:border-t-gray-700">
              <div className="flex flex-col justify-end gap-4 sm:flex-row">
                <button
                  type="button"
                  onClick={() => router.back()}
                  className="rounded-lg border border-gray-200 px-6 py-3 font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.projectId}
                  className="flex items-center justify-center gap-2 rounded-md border border-[#1D7BD7] bg-transparent px-4 py-2 whitespace-nowrap text-[#1D7BD7] transition-all hover:bg-[#1D7BD7] hover:text-white dark:hover:text-white"
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

type ProjectSelectorProps = {
  value: string
  defaultName: string
  onProjectChange: (id: string | null, name: string) => void
}

export const ProjectSelector = ({ value, defaultName, onProjectChange }: ProjectSelectorProps) => {
  const client = useApolloClient()
  const [searchText, setSearchText] = useState(defaultName || '')
  const [rawResults, setRawResults] = useState<{ id: string; name: string }[]>([])
  const [suggestions, setSuggestions] = useState<{ id: string; name: string }[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const suggestionClicked = useRef(false)
  const blurTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      if (!query.trim()) {
        setRawResults([])
        return
      }

      try {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query },
        })

        setRawResults(data.searchProjects || [])
        setShowSuggestions(true)
      } catch (err) {
        setRawResults([])
        setShowSuggestions(false)
        throw new Error('Error fetching suggestions:', err)
      }
    }, 300),
    [client]
  )

  // Trigger search suggestions on user input
  useEffect(() => {
    fetchSuggestions(searchText)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [searchText, fetchSuggestions])

  // Filter out selected project from results
  useEffect(() => {
    const filtered = rawResults.filter((proj) => proj.id !== value)
    setSuggestions(filtered.slice(0, 5))
  }, [rawResults, value])

  const handleSelect = (id: string, name: string) => {
    suggestionClicked.current = true
    setSearchText(name)
    setShowSuggestions(false)
    setError(null)
    onProjectChange(id, name)
  }

  const handleBlur = () => {
    blurTimeoutRef.current = setTimeout(() => {
      setShowSuggestions(false)

      if (!suggestionClicked.current && searchText.trim() && !value) {
        setError('Project not found. Please select a valid project from the list.')
      }

      suggestionClicked.current = false
    }, 150)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const input = e.target.value
    setSearchText(input)
    setError(null)

    if (value && input !== defaultName) {
      onProjectChange(null, input)
    }
  }

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (blurTimeoutRef.current) {
        clearTimeout(blurTimeoutRef.current)
      }
    }
  }, [])

  return (
    <div className="relative">
      <label htmlFor="projectSelector" className="mb-2 block text-sm font-medium">
        Project Name *
      </label>
      <input
        id="projectSelector"
        type="text"
        placeholder="Start typing project name..."
        value={searchText}
        required
        onChange={handleInputChange}
        onBlur={handleBlur}
        className={clsx(
          'w-full max-w-md rounded-lg border-2 bg-gray-50 px-4 py-3 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-hidden sm:w-96 dark:bg-gray-800 dark:text-gray-200 dark:focus:border-blue-400 dark:focus:ring-blue-400'
        )}
      />

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 mt-1 w-full rounded-md border border-gray-300 bg-white shadow-lg dark:bg-gray-700">
          {suggestions.map((project) => (
            <button
              key={project.id}
              type="button"
              onMouseDown={() => (suggestionClicked.current = true)}
              onClick={() => handleSelect(project.id, project.name)}
              className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
            >
              {project.name}
            </button>
          ))}
        </div>
      )}

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}
