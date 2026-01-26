'use client'

import { Button } from '@heroui/button'
import { Dropdown, DropdownItem, DropdownMenu, DropdownTrigger } from '@heroui/react'
import type React from 'react'
import { useState } from 'react'
import { FiDownload } from 'react-icons/fi'

export type ExportFormat = 'CSV' | 'JSON'

interface ExportButtonProps {
    onExport: (format: ExportFormat) => Promise<void>
    isDisabled?: boolean
    className?: string
}

/**
 * Export button component with format selection dropdown.
 * Shows loading state during export and handles format selection.
 */
const ExportButton: React.FC<ExportButtonProps> = ({ onExport, isDisabled = false, className }) => {
    const [isExporting, setIsExporting] = useState(false)

    const handleExport = async (format: ExportFormat) => {
        if (isExporting || isDisabled) return

        setIsExporting(true)
        try {
            await onExport(format)
        } finally {
            setIsExporting(false)
        }
    }

    return (
        <Dropdown>
            <DropdownTrigger>
                <Button
                    variant="bordered"
                    isLoading={isExporting}
                    isDisabled={isDisabled || isExporting}
                    startContent={!isExporting && <FiDownload className="h-4 w-4" />}
                    className={className}
                    aria-label="Export issues"
                >
                    Export
                </Button>
            </DropdownTrigger>
            <DropdownMenu
                aria-label="Export format options"
                onAction={(key) => handleExport(key as ExportFormat)}
                disabledKeys={isExporting ? ['CSV', 'JSON'] : []}
            >
                <DropdownItem
                    key="CSV"
                    description="Best for spreadsheets"
                    startContent={<span className="text-sm">📊</span>}
                >
                    Export as CSV
                </DropdownItem>
                <DropdownItem
                    key="JSON"
                    description="Best for developers"
                    startContent={<span className="text-sm">📄</span>}
                >
                    Export as JSON
                </DropdownItem>
            </DropdownMenu>
        </Dropdown>
    )
}

export default ExportButton
