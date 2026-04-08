'use client'

import type React from 'react'

interface FormTextareaProps {
  id: string
  name: string
  label: string
  placeholder: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void
  error?: string
  touched?: boolean
  rows?: number
  required?: boolean
}

export const FormTextarea = ({
  id,
  name,
  label,
  placeholder,
  value,
  onChange,
  error,
  touched,
  rows = 4,
  required = false,
}: FormTextareaProps) => {
  const hasError = touched && !!error

  return (
    <div className="w-full min-w-0 lg:col-span-2" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <div className="flex flex-col gap-2">
        <label htmlFor={id} className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          {label} {required && <span className="text-gray-500 dark:text-gray-400">*</span>}
        </label>
        <textarea
          id={id}
          name={name}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          rows={rows}
          required={required}
          className={`w-full min-w-0 rounded-lg border bg-gray-50 px-3 py-2 text-gray-800 shadow-sm placeholder:text-gray-400 focus:border-[#1D7BD7] focus:ring-1 focus:ring-[#1D7BD7] focus:outline-none dark:bg-gray-800 dark:text-gray-200 dark:focus:ring-[#1D7BD7] ${
            hasError ? 'border-red-500/70 dark:border-red-400/70' : 'border-gray-200 dark:border-gray-600'
          }`}
        />
        {hasError && (
          <p className="text-sm break-words whitespace-normal text-red-600 dark:text-red-400">{error}</p>
        )}
      </div>
    </div>
  )
}
