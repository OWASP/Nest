'use client'

import { Input } from '@heroui/react'

/** Calm invalid state: keep surface neutral, emphasize border + helper text (HeroUI defaults paint the whole field red). */
const COMMON_INPUT_CLASS_NAMES = {
  base: 'w-full min-w-0 group',
  label:
    'text-sm font-semibold !text-gray-600 dark:!text-gray-300 group-data-[invalid=true]:!text-gray-600 dark:group-data-[invalid=true]:!text-gray-300',
  input: 'text-gray-800 dark:text-gray-200',
  inputWrapper:
    'bg-gray-50 dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-600 group-data-[invalid=true]:!bg-gray-50 dark:group-data-[invalid=true]:!bg-gray-800 group-data-[invalid=true]:!border-red-500/70 dark:group-data-[invalid=true]:!border-red-400/70 group-data-[invalid=true]:shadow-none',
  helperWrapper: 'min-w-0 max-w-full w-full',
  errorMessage:
    'break-words whitespace-normal max-w-full w-full text-sm !text-red-600 dark:!text-red-400',
}

interface FormTextInputProps {
  id: string
  name: string
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
  autoComplete?: string
}

export const FormTextInput = ({
  id,
  name,
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
  autoComplete,
}: FormTextInputProps) => {
  return (
    <div className={className || 'w-full max-w-full min-w-0 overflow-hidden'}>
      <Input
        id={id}
        name={name}
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
        autoComplete={autoComplete}
        classNames={COMMON_INPUT_CLASS_NAMES}
      />
    </div>
  )
}
