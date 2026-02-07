'use client'

import { Input } from '@heroui/react'

const COMMON_INPUT_CLASS_NAMES = {
  base: 'w-full min-w-0',
  label: 'text-sm font-semibold text-gray-800 dark:text-gray-300',
  input: 'text-gray-800 dark:text-gray-200',
  inputWrapper: 'bg-gray-50 dark:bg-gray-800',
  helperWrapper: 'min-w-0 max-w-full w-full',
  errorMessage: 'break-words whitespace-normal max-w-full w-full',
}

interface FormTextInputProps {
  id: string
  type?: string
  label: string
  placeholder?: string
  value: string
  onValueChange: (value: string) => void
  error?: string
  touched?: boolean
  required?: boolean
  min?: number | string
  className?: string
  onBlur?: () => void
}

export const FormTextInput = ({
  id,
  type = 'text',
  label,
  placeholder,
  value,
  onValueChange,
  error,
  touched,
  required = false,
  min,
  className,
  onBlur,
}: FormTextInputProps) => {
  return (
    <div className={className || 'w-full min-w-0'} style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <Input
        id={id}
        type={type}
        label={label}
        labelPlacement="outside"
        placeholder={placeholder}
        value={value}
        onValueChange={onValueChange}
        onBlur={onBlur}
        isRequired={required}
        isInvalid={touched && !!error}
        errorMessage={touched ? error : undefined}
        min={min}
        classNames={COMMON_INPUT_CLASS_NAMES}
      />
    </div>
  )
}
