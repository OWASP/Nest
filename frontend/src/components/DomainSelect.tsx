import { Select, SelectItem } from '@heroui/select'
import React from 'react'

interface DomainSelectProps {
    value: string
    onChange: (value: string) => void
    error?: string
}

const AVAILABLE_DOMAINS = [
    'Software Engineering',
    'Data Science',
    'Product Management',
    'Design',
    'Security',
    'DevOps',
    'AI/ML',
    'Mobile Development',
    'Cloud Computing',
    'Blockchain',
    'Game Development',
    'Quality Assurance',
]

const DomainSelect = ({ value, onChange, error }: DomainSelectProps) => {
    const selectedKeys = value ? new Set(value.split(',').map((s) => s.trim()).filter(Boolean)) : new Set([])

    const handleSelectionChange = (keys: any) => {
        const selected = Array.from(keys).join(', ')
        onChange(selected)
    }

    return (
        <div>
            <label className="mb-2 block text-sm font-semibold text-gray-600 dark:text-gray-300">
                Domains
            </label>
            <Select
                label="Select domains"
                selectionMode="multiple"
                placeholder="Select domains"
                selectedKeys={selectedKeys}
                onSelectionChange={handleSelectionChange}
                className="max-w-xs"
                errorMessage={error}
                isInvalid={!!error}
            >
                {AVAILABLE_DOMAINS.map((domain) => (
                    <SelectItem key={domain} value={domain}>
                        {domain}
                    </SelectItem>
                ))}
            </Select>
        </div>
    )
}

export default DomainSelect
