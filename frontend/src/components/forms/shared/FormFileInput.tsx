'use client'

import type React from 'react'

interface FormFileInputProps {
  id: string
  label: string
  accept?: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  error?: string
  touched?: boolean
  required?: boolean
  selectedFile?: File | null
}

export const FormFileInput = ({
  id,
  label,
  accept,
  onChange,
  error,
  touched,
  required = false,
  selectedFile,
}: FormFileInputProps) => {
  const hasError = touched && !!error

  return (
    <div className="w-full min-w-0 lg:col-span-2" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <div className="flex flex-col gap-2">
        <label htmlFor={id} className="text-sm font-semibold text-gray-600 dark:text-gray-300">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <input
          id={id}
          type="file"
          onChange={onChange}
          accept={accept}
          required={required}
          className="w-full text-sm text-gray-700 file:mr-3 file:rounded file:border-0 file:bg-[#1D7BD7] file:px-3 file:py-1 file:text-sm file:text-white hover:file:bg-[#1a6ebd] dark:text-gray-200"
        />
        {selectedFile && <p className="truncate text-sm text-gray-500">{selectedFile.name}</p>}
        {hasError && <p className="text-sm break-words whitespace-normal text-red-500">{error}</p>}
      </div>
    </div>
  )
}
