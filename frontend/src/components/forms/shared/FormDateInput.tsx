'use client'

import { Input } from '@heroui/react'

const COMMON_INPUT_CLASS_NAMES = {
  base: 'w-full min-w-0',
  label: 'text-sm font-semibold text-gray-600 dark:text-gray-300',
  input: 'text-gray-800 dark:text-gray-200',
  inputWrapper: 'bg-gray-50 dark:bg-gray-800',
  helperWrapper: 'min-w-0 max-w-full w-full',
  errorMessage: 'break-words whitespace-normal max-w-full w-full',
}

interface FormDateInputProps {
  id: string
  label: string
  value: string
  onValueChange: (value: string) => void
  error?: string
  touched?: boolean
  required?: boolean
  min?: string
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
}: FormDateInputProps) => {
  return (
    <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <Input
        id={id}
        type="date"
        label={label}
        labelPlacement="outside"
        value={value}
        onValueChange={onValueChange}
        isRequired={required}
        isInvalid={touched && !!error}
        errorMessage={touched ? error : undefined}
        min={min}
        classNames={COMMON_INPUT_CLASS_NAMES}
      />
    </div>
  )
}
