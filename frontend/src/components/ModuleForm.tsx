'use client'
import { useApolloClient } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import debounce from 'lodash/debounce'
import type React from 'react'
import { useState, useEffect, useCallback } from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'
import type { ValidationErrors } from 'utils/helpers/handleGraphQLError'
import { FormButtons } from 'components/forms/shared/FormButtons'
import { FormDateInput } from 'components/forms/shared/FormDateInput'
import { FormTextarea } from 'components/forms/shared/FormTextarea'
import { FormTextInput } from 'components/forms/shared/FormTextInput'
import {
  getCommonValidationRules,
  validateDescription,
  validateEndDate,
  validateName,
  validateRequired,
  validateStartDate,
} from 'components/forms/shared/formValidationUtils'
import { useFormValidation } from 'components/forms/shared/useFormValidation'

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
  minDate?: string
  maxDate?: string
  validationErrors?: ValidationErrors
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
  minDate,
  maxDate,
  validationErrors,
}: ModuleFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const handleInputChange = (name: string, value: string) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSelectChange = (keys: React.Key | Set<React.Key> | 'all') => {
    let keySet: Set<React.Key>
    if (keys instanceof Set) {
      keySet = keys
    } else if (keys === 'all') {
      keySet = new Set()
    } else {
      keySet = new Set([keys])
    }
    const [value] = Array.from(keySet as Set<string>)
    if (value) {
      setFormData((prev) => ({ ...prev, experienceLevel: value }))
      setTouched((prev) => ({ ...prev, experienceLevel: true }))
    }
  }

  const validateNameLocal = (value: string): string | undefined => {
    if (validationErrors?.name) {
      return validationErrors.name
    }
    return validateName(value)
  }

  const validateEndDateLocal = (value: string): string | undefined => {
    return validateEndDate(value, formData.startedAt)
  }

  const validateProject = (projectId: string, projectName: string): string | undefined => {
    if (!projectId || !projectName.trim()) {
      return 'Project is required'
    }
    return undefined
  }

  const validateExperienceLevel = (value: string): string | undefined => {
    return validateRequired(value, 'Experience level')
  }

  const errors = useFormValidation(
    [
      ...getCommonValidationRules(formData, touched, validateNameLocal, validateEndDateLocal),
      {
        field: 'projectId',
        shouldValidate: touched.projectId ?? false,
        validator: () => validateProject(formData.projectId, formData.projectName),
      },
      {
        field: 'experienceLevel',
        shouldValidate: touched.experienceLevel ?? false,
        validator: () => validateExperienceLevel(formData.experienceLevel),
      },
    ],
    [formData, touched, validationErrors]
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const allFields = [
      'name',
      'description',
      'startedAt',
      'endedAt',
      'projectId',
      'experienceLevel',
    ]
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    setTouched(newTouched)

    const nameError = validateName(formData.name)
    const descriptionError = validateDescription(formData.description)
    const startDateError = validateStartDate(formData.startedAt)
    const endDateError = validateEndDateLocal(formData.endedAt)
    const projectError = validateProject(formData.projectId, formData.projectName)
    const experienceLevelError = validateExperienceLevel(formData.experienceLevel)

    if (
      nameError ||
      descriptionError ||
      startDateError ||
      endDateError ||
      projectError ||
      experienceLevelError
    ) {
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
                <FormTextInput
                  id="module-name"
                  label="Name"
                  placeholder="Enter module name"
                  value={formData.name}
                  onValueChange={(value) => {
                    handleInputChange('name', value)
                    setTouched((prev) => ({ ...prev, name: true }))
                  }}
                  error={errors.name || validationErrors?.name}
                  touched={touched.name}
                  required
                  className="w-full min-w-0 lg:col-span-2"
                />

                <FormTextarea
                  id="module-description"
                  label="Description"
                  placeholder="Enter module description"
                  value={formData.description}
                  onChange={(e) => {
                    handleInputChange('description', e.target.value)
                    setTouched((prev) => ({ ...prev, description: true }))
                  }}
                  error={errors.description}
                  touched={touched.description}
                  required
                />
              </div>
            </section>

            {/* Configuration */}
            <section className="flex flex-col gap-6 text-gray-600 dark:text-gray-300">
              <div className="module-config-grid grid gap-6">
                <FormDateInput
                  id="module-start-date"
                  label="Start Date"
                  value={formData.startedAt}
                  onValueChange={(value) => {
                    handleInputChange('startedAt', value)
                    setTouched((prev) => ({ ...prev, startedAt: true }))
                  }}
                  error={errors.startedAt}
                  touched={touched.startedAt}
                  required
                  min={minDate}
                  max={maxDate}
                />
                <FormDateInput
                  id="module-end-date"
                  label="End Date"
                  value={formData.endedAt}
                  onValueChange={(value) => {
                    handleInputChange('endedAt', value)
                    setTouched((prev) => ({ ...prev, endedAt: true }))
                  }}
                  error={errors.endedAt}
                  touched={touched.endedAt}
                  required
                  min={formData.startedAt || minDate || undefined}
                  max={maxDate}
                />
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Select
                    id="experienceLevel"
                    label="Experience Level"
            
                    selectedKeys={
                      formData.experienceLevel ? new Set([formData.experienceLevel]) : new Set()
                    }
                    onSelectionChange={handleSelectChange}
                    isRequired
                    isInvalid={touched.experienceLevel && !!errors.experienceLevel}
                    errorMessage={touched.experienceLevel ? errors.experienceLevel : undefined}
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
                <FormTextInput
                  id="module-domains"
                  label="Domains"
                  placeholder="AI, Web Development"
                  value={formData.domains}
                  onValueChange={(value) => handleInputChange('domains', value)}
                />
                <FormTextInput
                  id="module-tags"
                  label="Tags"
                  placeholder="javascript, react"
                  value={formData.tags}
                  onValueChange={(value) => handleInputChange('tags', value)}
                />
                <FormTextInput
                  id="module-labels"
                  label="Labels"
                  placeholder="good first issue, bug, enhancement"
                  value={formData.labels}
                  onValueChange={(value) => handleInputChange('labels', value)}
                />
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
                      setTouched((prev) => ({ ...prev, projectId: true }))
                    }}
                    isInvalid={touched.projectId && !!errors.projectId}
                    errorMessage={touched.projectId ? errors.projectId : undefined}
                  />
                </div>
                {isEdit && (
                  <FormTextInput
                    id="module-mentor-logins"
                    label="Mentor GitHub Usernames"
                    placeholder="johndoe, jane-doe"
                    value={formData.mentorLogins}
                    onValueChange={(value) => handleInputChange('mentorLogins', value)}
                    className="w-full min-w-0 lg:col-span-2"
                  />
                )}
              </div>
            </section>

            <FormButtons loading={loading} submitText={submitText} />
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
  const [isOpen, setIsOpen] = useState(false)
  const [focusedIndex, setFocusedIndex] = useState(-1)

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
        setFocusedIndex(-1)
        return
      }

      setIsLoading(true)
      try {
        const { data } = await client.query({
          query: SearchProjectNamesDocument,
          variables: { query: trimmedQuery },
        })

        const projects = data?.searchProjects || []
        const filtered = projects.filter((proj) => proj.id !== value)
        setItems(filtered.slice(0, 5))
        setIsOpen(filtered.length > 0)
        setFocusedIndex(-1)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error(
          'Error fetching project suggestions:',
          err instanceof Error ? err.message : String(err),
          err
        )
        setItems([])
      } finally {
        setIsLoading(false)
      }
    }, 300),
    [client, value]
  )

  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const handleSelect = (project: { id: string; name: string }) => {
    setInputValue(project.name)
    setItems([])
    setIsOpen(false)
    onProjectChange(project.id, project.name)
  }

  const handleInputChange = (newValue: string) => {
    setInputValue(newValue)
    onProjectChange(null, newValue)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || items.length === 0) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setFocusedIndex((prev) => (prev + 1) % items.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setFocusedIndex((prev) => (prev <= 0 ? items.length - 1 : prev - 1))
    } else if (e.key === 'Enter' && focusedIndex >= 0 && focusedIndex < items.length) {
      e.preventDefault()
      handleSelect(items[focusedIndex])
      setFocusedIndex(-1)
    } else if (e.key === 'Escape') {
      setIsOpen(false)
      setFocusedIndex(-1)
    }
  }

  const displayError = errorMessage
  const shouldShowInvalid = isInvalid

  return (
    <div data-testid="autocomplete" className="relative w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <label
        htmlFor="projectSelector"
        className="mb-1 block text-sm font-semibold text-gray-600 dark:text-gray-300"
      >
        Project Name<span aria-hidden="true"> *</span>
      </label>
      <input
        id="projectSelector"
        type="text"
        data-testid="autocomplete-input"
        placeholder="Start typing project name..."
        value={inputValue}
        onChange={(e) => handleInputChange(e.target.value)}
        onKeyDown={handleKeyDown}
        required
        aria-invalid={shouldShowInvalid}
        aria-describedby={shouldShowInvalid ? 'projectSelector-error' : undefined}
        aria-autocomplete="list"
        aria-expanded={isOpen}
        aria-activedescendant={focusedIndex >= 0 ? `project-option-${focusedIndex}` : undefined}
        role="combobox"
        aria-controls="projectSelector-listbox"
        aria-haspopup="listbox"
        className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
      />
      <button
        type="button"
        data-testid="autocomplete-clear"
        aria-label="Clear project selection"
        className="hidden"
        onClick={() => { setInputValue(''); setItems([]); setIsOpen(false); onProjectChange(null, '') }}
      />
      {isLoading && (
        <p className="mt-1 text-xs text-gray-500">Loading...</p>
      )}
      {isOpen && items.length > 0 && (
        <ul role="listbox" id="projectSelector-listbox" className="absolute z-50 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          {items.map((project, index) => (
            <li
              key={project.id}
              id={`project-option-${index}`}
              role="option"
              aria-selected={focusedIndex === index}
              tabIndex={0}
              data-testid="autocomplete-item"
              data-text-value={project.name}
              onClick={() => { handleSelect(project); setFocusedIndex(-1) }}
              onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handleSelect(project); setFocusedIndex(-1) } }}
              className={`cursor-pointer px-3 py-2 text-sm text-gray-800 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700 ${focusedIndex === index ? 'bg-gray-100 dark:bg-gray-700' : ''}`}
            >
              {project.name}
            </li>
          ))}
        </ul>
      )}
      {shouldShowInvalid && displayError && (
        <p id="projectSelector-error" data-testid="autocomplete-error" className="mt-1 break-words text-xs text-red-500">
          {displayError}
        </p>
      )}
    </div>
  )
}
