import { useState } from 'react'

interface UseFormProps<T> {
    initialValues: T
    validate?: (values: T) => Partial<Record<keyof T, string>>
    onSubmit: (values: T) => Promise<void>
}

export const useForm = <T extends Record<string, any>>({ initialValues, validate, onSubmit }: UseFormProps<T>) => {
    const [values, setValues] = useState<T>(initialValues)
    const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({})
    const [isSubmitting, setIsSubmitting] = useState(false)

    const handleChange = (name: keyof T, value: any) => {
        setValues((prev) => ({ ...prev, [name]: value }))
        // Clear error when modified
        if (errors[name]) {
            setErrors((prev) => ({ ...prev, [name]: undefined }))
        }
    }

    const handleSubmit = async (e?: React.FormEvent) => {
        if (e) e.preventDefault()
        setIsSubmitting(true)
        setErrors({})

        if (validate) {
            const validationErrors = validate(values)
            // Filter out undefined/null errors
            const activeErrors = Object.entries(validationErrors).reduce((acc, [key, val]) => {
                if (val) acc[key as keyof T] = val
                return acc
            }, {} as Partial<Record<keyof T, string>>)

            if (Object.keys(activeErrors).length > 0) {
                setErrors(activeErrors)
                setIsSubmitting(false)
                return
            }
        }

        try {
            await onSubmit(values)
        } finally {
            setIsSubmitting(false)
        }
    }

    return { values, errors, isSubmitting, handleChange, handleSubmit, setValues, setErrors }
}
