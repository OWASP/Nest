'use client'
import { Button } from '@heroui/button'
import { useRouter } from 'next/navigation'

interface FormButtonsProps {
  loading: boolean
  submitText?: string
  onCancel?: () => void
}

export const FormButtons = ({ loading, submitText = 'Save', onCancel }: FormButtonsProps) => {
  const router = useRouter()

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    } else {
      router.back()
    }
  }

  return (
    <div className="border-t border-gray-200 pt-8 text-gray-600 dark:border-gray-700 dark:text-gray-300">
      <div className="flex flex-col justify-end gap-4 sm:flex-row">
        <Button
          type="button"
          variant="bordered"
          onPress={handleCancel}
          className="rounded-md border border-gray-300 px-4 py-2 font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Cancel
        </Button>
        <Button type="submit" color="primary" isDisabled={loading} className="font-medium">
          {loading ? 'Saving...' : submitText}
        </Button>
      </div>
    </div>
  )
}
