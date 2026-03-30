'use client'

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
  const isInvalid = touched && !!error

  return (
    <div className="w-full min-w-0" style={{ maxWidth: '100%', overflow: 'hidden' }}>
      <label
        htmlFor={id}
        className="mb-1 block text-sm font-semibold text-gray-600 dark:text-gray-300"
      >
        {label}
      </label>
      {required && <span aria-hidden="true" className="ml-1 text-red-500">*</span>}
      <input
        id={id}
        type="date"
        value={value}
        onChange={(e) => onValueChange(e.target.value)}
        required={required}
        aria-invalid={isInvalid}
        aria-describedby={isInvalid ? `${id}-error` : undefined}
        min={min}
        max={max}
        className="w-full rounded-md border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
      />
      {isInvalid && (
        <p id={`${id}-error`} data-testid="error-message" className="mt-1 break-words text-xs text-red-500">
          {error}
        </p>
      )}
    </div>
  )
}
