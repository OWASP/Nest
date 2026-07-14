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
        className="w-full min-w-0"
      >
        <Label htmlFor={id} className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          {label}
        </Label>
        <Input.Root className="w-full bg-gray-50 dark:bg-gray-800">
          <Input
            id={id}
            type="date"
            min={min}
            max={max}
            className="text-gray-800 dark:text-gray-200"
          />
        </Input.Root>
        {touched && error && (
          <FieldError className="w-full max-w-full break-words text-sm text-red-500">
            {error}
          </FieldError>
        )}
      </TextField>
    </div>
  )
}
