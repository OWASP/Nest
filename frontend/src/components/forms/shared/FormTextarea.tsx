'use client'

import type React from 'react'

interface FormTextareaProps {
  id: string
  label: string
  placeholder: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  error?: string
  touched?: boolean
  rows?: number
  required?: boolean
  maxLength?: number
  showCharCount?: boolean
}

export const FormTextarea = ({
  id,
  label,
  placeholder,
  value,
  onChange,
  error,
  touched,
  rows = 4,
  required = false,
  maxLength,
  showCharCount = false,
}: FormTextareaProps) => {
  const charCount = value.length
  const isNearLimit = maxLength !== undefined && charCount >= maxLength - 20
  const isAtLimit = maxLength !== undefined && charCount >= maxLength
  const hasError = touched && !!error
  const counterColorClass = isAtLimit
    ? 'text-red-500'
    : isNearLimit
      ? 'text-amber-500'
      : 'text-gray-400 dark:text-gray-500'

  return (
    <div className="w-full min-w-0 lg:col-span-2" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <div className="flex flex-col gap-2">
        <label htmlFor={id} className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <textarea
          id={id}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          rows={rows}
          required={required}
          maxLength={maxLength}
          className={`w-full min-w-0 rounded-lg border px-3 py-2 text-gray-800 placeholder:text-gray-400 focus:border-[#1D7BD7] focus:ring-1 focus:ring-[#1D7BD7] focus:outline-none dark:bg-gray-800 dark:text-gray-200 dark:focus:ring-[#1D7BD7] ${
            hasError ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
          }`}
        />
        {showCharCount && maxLength !== undefined && (
          <p className={`text-right text-xs font-medium transition-colors ${counterColorClass}`}>
            {charCount}/{maxLength} characters
            {isAtLimit && <span className="ml-1 font-semibold">- limit reached</span>}
          </p>
        )}
        {hasError && <p className="text-sm break-words whitespace-normal text-red-500">{error}</p>}
      </div>
    </div>
  )
}
