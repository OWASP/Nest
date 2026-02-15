'use client'
import { useApolloClient } from '@apollo/client/react'
import { Autocomplete, AutocompleteItem } from '@heroui/react'
import { Select, SelectItem } from '@heroui/select'
import debounce from 'lodash/debounce'
import type React from 'react'
import { useState, useEffect, useCallback } from 'react'
import { ExperienceLevelEnum } from 'types/__generated__/graphql'
import { GetModulesByProgramDocument } from 'types/__generated__/moduleQueries.generated'
import { SearchProjectNamesDocument } from 'types/__generated__/projectQueries.generated'
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
  programKey: string
  currentModuleKey?: string
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
  programKey,
  currentModuleKey,
}: ModuleFormProps) => {
  const client = useApolloClient()
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [nameUniquenessError, setNameUniquenessError] = useState<string | undefined>(undefined)

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

  const validateNameWithUniqueness = (
    value: string,
    uniquenessError?: string | undefined
  ): string | undefined => {
    return validateName(value, uniquenessError)
  }

  const validateNameLocal = (value: string): string | undefined => {
    if (nameUniquenessError) {
      return nameUniquenessError
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

  const checkNameUniqueness = useCallback(
    async (name: string): Promise<string | undefined> => {
      if (!name.trim()) {
        return undefined
      }

      try {
        const { data } = await client.query({
          query: GetModulesByProgramDocument,
          variables: { programKey },
          fetchPolicy: 'network-only',
        })

        const modules = data?.getProgramModules || []
        const duplicateModule = modules.find(
          (module: { name: string; key: string }) =>
            module.name.toLowerCase() === name.trim().toLowerCase() &&
            (!isEdit || module.key !== currentModuleKey)
        )

        if (duplicateModule) {
          return 'This module name already exists in this program'
        }
        return undefined
      } catch {
        // Silently fail uniqueness check - backend will catch it
        return undefined
      }
    },
    [client, programKey, isEdit, currentModuleKey]
  )

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
    [formData, touched, nameUniquenessError]
  )

  const handleSubmit = async (e: React.FormEvent) => {
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

    let uniquenessError: string | undefined
    if (formData.name.trim()) {
      uniquenessError = await checkNameUniqueness(formData.name)
      setNameUniquenessError(uniquenessError)
      if (uniquenessError) {
        setTouched((prev) => ({ ...prev, name: true }))
      }
    } else {
      setNameUniquenessError(undefined)
    }

    const nameError = validateNameWithUniqueness(formData.name, uniquenessError)
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
                    if (nameUniquenessError) {
                      setNameUniquenessError(undefined)
                    }
                  }}
                  error={errors.name || nameUniquenessError}
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
                    labelPlacement="outside"
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

        const projects = data?.searchProjects || []
        const filtered = projects.filter((proj) => proj.id !== value)
        setItems(filtered.slice(0, 5))
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

  // Trigger search suggestions on user input
  useEffect(() => {
    fetchSuggestions(inputValue)
    return () => {
      fetchSuggestions.cancel()
    }
  }, [inputValue, fetchSuggestions])

  const handleSelectionChange = (keys: React.Key | null) => {
    if (keys === null) return
    const selectedKey = keys as string
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
        clearButtonProps={{
          'aria-label': 'clear selected project',
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
