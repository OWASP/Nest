'use client'

import { FieldError, Input, Label, TextField } from '@heroui/react'

interface FormDateInputProps {
  id: string
  label: string
  value: string
  onValueChange: (value: string) => void
  error?: string
  touched?: boolean
  required?: boolean
  min?: string
  max?: string
}

export const FormDateInput = ({
  id,
  label,
  value,
  onValueChange,
  error,
  touched,
  required = false,
  min,
  max,
}: FormDateInputProps) => {
  return (
    <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <TextField
        id={id}
        isRequired={required}
        isInvalid={touched && !!error}
        value={value}
        onChange={onValueChange}
      >
        <Label htmlFor={id} className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          {label}
        </Label>
        <Input
          id={id}
          type="date"
          min={min}
          max={max}
          className="w-full min-w-0 bg-gray-50 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
        />
        {touched && error && (
          <FieldError className="w-full max-w-full text-sm break-words text-red-500">
            {error}
          </FieldError>
        )}
      </TextField>
    </div>
  )
}
