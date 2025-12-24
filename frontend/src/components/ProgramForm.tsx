'use client'

import { useApolloClient } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Input } from '@heroui/react'
import type React from 'react'
import { useState, useMemo, useCallback } from 'react'
import { GetMyProgramsDocument } from 'types/__generated__/programsQueries.generated'

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
  currentProgramKey?: string
}

const ProgramForm = ({
  formData,
  setFormData,
  onSubmit,
  loading,
  title,
  isEdit,
  submitText = 'Save',
  currentProgramKey,
}: ProgramFormProps) => {
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [nameUniquenessError, setNameUniquenessError] = useState<string | undefined>(undefined)
  const client = useApolloClient()

  const handleInputChange = (name: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (name === 'name') {
      setNameUniquenessError(undefined)
    }
  }

  const validateName = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Name is required'
    }
    if (value.length > 200) {
      return 'Name must be 200 characters or less'
    }
    if (nameUniquenessError) {
      return nameUniquenessError
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
    if (formData.startedAt && new Date(value) <= new Date(formData.startedAt)) {
      return 'End date must be after start date'
    }
    return undefined
  }

  const validateMenteesLimit = (value: number | string): string | undefined => {
    const numValue = typeof value === 'string' ? Number(value) : value
    if (numValue < 0) {
      return 'Mentees limit cannot be negative'
    }
    if (!Number.isInteger(numValue)) {
      return 'Mentees limit must be a whole number'
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
    if (touched.menteesLimit) {
      errs.menteesLimit = validateMenteesLimit(formData.menteesLimit)
    }
    return errs
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formData, touched, nameUniquenessError])

  const checkNameUniquenessSync = useCallback(
    async (name: string): Promise<string | undefined> => {
      if (!name.trim()) {
        return undefined
      }

      try {
        const { data } = await client.query({
          query: GetMyProgramsDocument,
          variables: { search: name.trim(), page: 1, limit: 100 },
        })

        const programs = data?.myPrograms?.programs || []
        const duplicateProgram = programs.find(
          (program: { name: string; key: string }) =>
            program.name.toLowerCase() === name.trim().toLowerCase() &&
            (!isEdit || program.key !== currentProgramKey)
        )

        if (duplicateProgram) {
          return 'A program with this name already exists'
        }
        return undefined
      } catch {
        // Silently fail uniqueness check - backend will catch it
        return undefined
      }
    },
    [client, isEdit, currentProgramKey]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const allFields = ['name', 'description', 'startedAt', 'endedAt']
    const newTouched: Record<string, boolean> = {}
    allFields.forEach((field) => {
      newTouched[field] = true
    })
    if (formData.menteesLimit !== undefined && formData.menteesLimit !== null) {
      newTouched.menteesLimit = true
    }
    setTouched(newTouched)

    if (formData.name.trim()) {
      const uniquenessError = await checkNameUniquenessSync(formData.name)
      if (uniquenessError) {
        setNameUniquenessError(uniquenessError)
      }
    }

    // Validate all required fields
    const nameError = validateName(formData.name)
    const descriptionError = validateDescription(formData.description)
    const startDateError = validateStartDate(formData.startedAt)
    const endDateError = validateEndDate(formData.endedAt)
    const menteesLimitError =
      touched.menteesLimit || formData.menteesLimit !== undefined
        ? validateMenteesLimit(formData.menteesLimit)
        : undefined

    // Prevent submission if any validation errors exist
    if (nameError || descriptionError || startDateError || endDateError || menteesLimitError) {
      return
    }

    onSubmit(e)
  }

  return (
    <div className="text-text program-form-container flex min-h-screen w-full flex-col items-center justify-normal p-5">
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
                    id="program-name"
                    type="text"
                    label="Name"
                    labelPlacement="outside"
                    placeholder="Enter program name"
                    value={formData.name}
                    onValueChange={(value) => {
                      handleInputChange('name', value)
                      setTouched((prev) => ({ ...prev, name: true }))
                    }}
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
                      htmlFor="program-description"
                      className="text-sm font-semibold text-gray-600 dark:text-gray-300"
                    >
                      Description <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      id="program-description"
                      placeholder="Enter program description"
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
              <div className="config-grid grid gap-6">
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="program-start-date"
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
                    id="program-end-date"
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
                  <Input
                    id="mentees-limit"
                    type="number"
                    label="Mentees Limit"
                    labelPlacement="outside"
                    placeholder="Enter mentees limit (0 for unlimited)"
                    value={formData.menteesLimit.toString()}
                    onValueChange={(value) => handleInputChange('menteesLimit', Number(value) || 0)}
                    isInvalid={touched.menteesLimit && !!errors.menteesLimit}
                    errorMessage={touched.menteesLimit ? errors.menteesLimit : undefined}
                    min={0}
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
              </div>
            </section>

            {/* Additional Details */}
            <section className="flex flex-col gap-6">
              <div className="grid grid-cols-1 gap-6 text-gray-600 lg:grid-cols-2 dark:text-gray-300">
                <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
                  <Input
                    id="program-tags"
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
                    id="program-domains"
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
                {isEdit && (
                  <div
                    className="w-full min-w-0 lg:col-span-2"
                    style={{ maxWidth: '100%', overflow: 'hidden' }}
                  >
                    <Input
                      id="admin-github-usernames"
                      type="text"
                      label="Admin GitHub Usernames"
                      labelPlacement="outside"
                      placeholder="johndoe, jane-doe"
                      value={formData.adminLogins || ''}
                      onValueChange={(value) => handleInputChange('adminLogins', value)}
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
                  onPress={() => history.back()}
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

export default ProgramForm
