'use client'
import { useApolloClient } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Autocomplete, AutocompleteItem, Input } from '@heroui/react'
import { Select, SelectItem } from '@heroui/select'
import debounce from 'lodash/debounce'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useEffect, useCallback, useMemo } from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'

interface ModuleFormProps {
  formData: {
    description: string
    domains: string
    endedAt: string
    experienceLevel: string
    labels: string
    mentorLogins: string
    name: string
    projectId: string
    projectName: string
    startedAt: string
    tags: string
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
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const handleInputChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (keys: React.Key | Set<React.Key> | 'all') => {
    const keySet = keys instanceof Set ? keys : keys === 'all' ? new Set() : new Set([keys])
    const [value] = Array.from(keySet as Set<string>)
    if (value) {
      setFormData((prev) => ({ ...prev, experienceLevel: value }))
    }
  }

  const validateName = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Name is required'
    }
    if (value.length > 200) {
      return 'Name must be 200 characters or less'
    }
    return undefined
  }

  const validateDescription = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Description is required'
    }
    return undefined
  }

  const validateStartDate = (value: string): string | undefined => {
    if (!value) {
      return 'Start date is required'
    }
    return undefined
  }

  const validateEndDate = (value: string): string | undefined => {
    if (!value) {
      return 'End date is required'
    }
    if (formData.startedAt && value && new Date(value) <= new Date(formData.startedAt)) {
      return 'End date must be after start date'
    }
    return undefined
  }

  const validateProject = (projectId: string, projectName: string): string | undefined => {
    if (!projectId || !projectName.trim()) {
      return 'Project is required'
    }
    return undefined
  }

  const errors = useMemo(() => {
    const errs: Record<string, string | undefined> = {}
    if (touched.name) {
      errs.name = validateName(formData.name)
    }
    if (touched.description) {
      errs.description = validateDescription(formData.description)
    }
    if (touched.startedAt) {
      errs.startedAt = validateStartDate(formData.startedAt)
    }
    if (touched.endedAt || (touched.startedAt && formData.endedAt)) {
      errs.endedAt = validateEndDate(formData.endedAt)
    }
    if (touched.projectId) {
      errs.projectId = validateProject(formData.projectId, formData.projectName)
    }
    return errs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData, touched])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const allFields = ['name', 'description', 'startedAt', 'endedAt', 'projectId']
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    setTouched(newTouched)

    // Validate all required fields
    const nameError = validateName(formData.name)
    const descriptionError = validateDescription(formData.description)
    const startDateError = validateStartDate(formData.startedAt)
    const endDateError = validateEndDate(formData.endedAt)
    const projectError = validateProject(formData.projectId, formData.projectName)

    if (nameError || descriptionError || startDateError || endDateError || projectError) {
      return
    }

    onSubmit(e)
  }

  return (
    <div className="text-text module-form-container flex w-full flex-col items-center justify-normal p-5">
      <div className="mb-8 text-left">
        <h1 className="mb-2 text-4xl font-bold text-gray-800 dark:text-gray-200">{title}</h1>
      </div>

      <div className="w-full max-w-4xl overflow-hidden rounded-2xl bg-white shadow-2xl dark:bg-[#212529]">
        <form onSubmit={handleSubmit} noValidate>
          <div className="flex flex-col gap-8 p-8">
            {/* Basic Information */}
            <section className="flex flex-col gap-6">
              <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
                <div
                  className="w-full min-w-0 lg:col-span-2"
                  style={{ maxWidth: '100%', overflow: 'hidden' }}
                >
                  <Input
                    id="module-name"
                    type="text"
                    label="Name"
                    labelPlacement="outside"
                    placeholder="Enter module name"
                    value={formData.name}
                    onValueChange={(value) => handleInputChange('name', value)}
                    isRequired
                    isInvalid={touched.name && !!errors.name}
                    errorMessage={touched.name ? errors.name : undefined}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>

                <div
                  className="w-full min-w-0 lg:col-span-2"
                  style={{ maxWidth: '100%', overflow: 'hidden' }}
                >
                  <div className="flex flex-col gap-2">
                    <label
                      htmlFor="module-description"
                      className="text-sm font-semibold text-gray-600 dark:text-gray-300"
                    >
                      Description <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="module-description"
                      placeholder="Enter module description"
                      value={formData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      rows={4}
                      required
                      className={`w-full min-w-0 rounded-lg border px-3 py-2 text-gray-800 placeholder:text-gray-400 focus:border-[#1D7BD7] focus:ring-1 focus:ring-[#1D7BD7] focus:outline-none dark:bg-gray-800 dark:text-gray-200 dark:focus:ring-[#1D7BD7] ${
                        touched.description && errors.description
                          ? 'border-red-500 dark:border-red-500'
                          : 'border-gray-300 dark:border-gray-600'
                      }`}
                    />
                    {touched.description && errors.description && (
                      <p className="text-sm break-words whitespace-normal text-red-500">
                        {errors.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </section>

            {/* Configuration */}
            <section className="flex flex-col gap-6 text-gray-600 dark:text-gray-300">
              <div className="module-config-grid grid gap-6">
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="module-start-date"
                    type="date"
                    label="Start Date"
                    labelPlacement="outside"
                    value={formData.startedAt}
                    onValueChange={(value) => handleInputChange('startedAt', value)}
                    isRequired
                    isInvalid={touched.startedAt && !!errors.startedAt}
                    errorMessage={touched.startedAt ? errors.startedAt : undefined}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="module-end-date"
                    type="date"
                    label="End Date"
                    labelPlacement="outside"
                    value={formData.endedAt}
                    onValueChange={(value) => handleInputChange('endedAt', value)}
                    isRequired
                    isInvalid={touched.endedAt && !!errors.endedAt}
                    errorMessage={touched.endedAt ? errors.endedAt : undefined}
                    min={formData.startedAt || undefined}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Select
                    id="experienceLevel"
                    label="Experience Level"
                    labelPlacement="outside"
                    selectedKeys={
                      formData.experienceLevel ? new Set([formData.experienceLevel]) : new Set()
                    }
                    onSelectionChange={handleSelectChange}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      trigger: 'bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-gray-200',
                      value: 'text-gray-800 dark:text-gray-200',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  >
                    {EXPERIENCE_LEVELS.map((lvl) => (
                      <SelectItem key={lvl.key}>{lvl.label}</SelectItem>
                    ))}
                  </Select>
                </div>
              </div>
            </section>

            {/* Additional Details */}
            <section className="flex flex-col gap-6">
              <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="module-domains"
                    type="text"
                    label="Domains"
                    labelPlacement="outside"
                    placeholder="AI, Web Development"
                    value={formData.domains}
                    onValueChange={(value) => handleInputChange('domains', value)}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="module-tags"
                    type="text"
                    label="Tags"
                    labelPlacement="outside"
                    placeholder="javascript, react"
                    value={formData.tags}
                    onValueChange={(value) => handleInputChange('tags', value)}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="module-labels"
                    type="text"
                    label="Labels"
                    labelPlacement="outside"
                    placeholder="good first issue, bug, enhancement"
                    value={formData.labels}
                    onValueChange={(value) => handleInputChange('labels', value)}
                    classNames={{
                      base: 'w-full min-w-0',
                      label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                      input: 'text-gray-800 dark:text-gray-200',
                      inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                      helperWrapper: 'min-w-0 max-w-full w-full',
                      errorMessage: 'break-words whitespace-normal max-w-full w-full',
                    }}
                  />
                </div>
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <ProjectSelector
                    value={formData.projectId}
                    defaultName={formData.projectName}
                    onProjectChange={(id, name) => {
                      setFormData((prev) => ({
                        ...prev,
                        projectId: id ?? '',
                        projectName: name,
                      }))
                    }}
                    isInvalid={touched.projectId && !!errors.projectId}
                    errorMessage={touched.projectId ? errors.projectId : undefined}
                  />
                </div>
                {isEdit && (
                  <div
                    className="w-full min-w-0 lg:col-span-2"
                    style={{ maxWidth: '100%', overflow: 'hidden' }}
                  >
                    <Input
                      id="module-mentor-logins"
                      type="text"
                      label="Mentor GitHub Usernames"
                      labelPlacement="outside"
                      placeholder="johndoe, jane-doe"
                      value={formData.mentorLogins}
                      onValueChange={(value) => handleInputChange('mentorLogins', value)}
                      classNames={{
                        base: 'w-full min-w-0',
                        label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
                        input: 'text-gray-800 dark:text-gray-200',
                        inputWrapper: 'bg-gray-50 dark:bg-gray-800',
                        helperWrapper: 'min-w-0 max-w-full w-full',
                        errorMessage: 'break-words whitespace-normal max-w-full w-full',
                      }}
                    />
                  </div>
                )}
              </div>
            </section>

            {/* Submit Buttons */}
            <div className="border-t border-gray-200 pt-8 text-gray-600 dark:border-gray-700 dark:text-gray-300">
              <div className="flex flex-col justify-end gap-4 sm:flex-row">
                <Button
                  type="button"
                  variant="bordered"
                  onPress={() => router.back()}
                  className="font-medium"
                >
                  Cancel
                </Button>
                <Button type="submit" isDisabled={loading} color="primary" className="font-medium">
                  {loading ? 'Saving...' : submitText}
                </Button>
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
  isInvalid?: boolean
  errorMessage?: string
}

export const ProjectSelector = ({
  value,
  defaultName,
  onProjectChange,
  isInvalid,
  errorMessage,
}: ProjectSelectorProps) => {
  const client = useApolloClient()
  const [inputValue, setInputValue] = useState(defaultName || '')
  const [items, setItems] = useState<{ id: string; name: string }[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (value && defaultName && defaultName !== inputValue) {
      setInputValue(defaultName)
    } else if (!value && !defaultName && inputValue) {
      setInputValue('')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultName, value])

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const fetchSuggestions = useCallback(
    debounce(async (query: string) => {
      const trimmedQuery = query.trim()
      if (trimmedQuery.length < 2) {
        setItems([])
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      try {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query: trimmedQuery },
        })

        const projects = data.searchProjects || []
        const filtered = projects.filter((proj) => proj.id !== value)
        setItems(filtered.slice(0, 5))
      } catch {
        setItems([])
      } finally {
        setIsLoading(false)
      }
    }, 300),
    [client, value]
  )

  // Trigger search suggestions on user input
  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const handleSelectionChange = (keys: React.Key | Set<React.Key> | 'all') => {
    const keySet = keys instanceof Set ? keys : keys === 'all' ? new Set() : new Set([keys])
    const selectedKey = Array.from(keySet as Set<string>)[0]
    if (selectedKey) {
      const selectedProject = items.find((item) => item.id === selectedKey)
      if (selectedProject) {
        setInputValue(selectedProject.name)
        onProjectChange(selectedProject.id, selectedProject.name)
      }
    } else {
      // Selection cleared
      setInputValue('')
      onProjectChange(null, '')
    }
  }

  const handleInputChange = (newValue: string) => {
    setInputValue(newValue)
    onProjectChange(null, newValue)
  }

  // Don't show validation error while user is actively typing (has text but no project selected)
  const isTyping = inputValue.trim() !== '' && !value
  const displayError = isTyping ? undefined : errorMessage
  const shouldShowInvalid = isTyping ? false : isInvalid

  return (
    <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <Autocomplete
        id="projectSelector"
        label="Project Name"
        labelPlacement="outside"
        placeholder="Start typing project name..."
        inputValue={inputValue}
        selectedKey={value || null}
        onInputChange={handleInputChange}
        onSelectionChange={handleSelectionChange}
        menuTrigger="input"
        isRequired
        isInvalid={shouldShowInvalid}
        errorMessage={displayError}
        isLoading={isLoading}
        allowsCustomValue={false}
        classNames={{
          base: 'w-full min-w-0',
          selectorButton: 'hidden',
        }}
        inputProps={{
          classNames: {
            label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
            input: 'text-gray-800 dark:text-gray-200',
            inputWrapper: 'bg-gray-50 dark:bg-gray-800',
            helperWrapper: 'min-w-0 max-w-full w-full',
            errorMessage: 'break-words whitespace-normal max-w-full w-full',
          },
        }}
      >
        {items.map((project) => (
          <AutocompleteItem key={project.id} textValue={project.name}>
            {project.name}
          </AutocompleteItem>
        ))}
      </Autocomplete>
    </div>
  )
}
