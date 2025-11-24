'use client'

import { faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'

interface ModuleActionsProps {
    moduleKey: string
    programKey: string
}

const ModuleActions: React.FC<ModuleActionsProps> = ({ moduleKey, programKey }) => {
    const router = useRouter()
    const [dropdownOpen, setDropdownOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    const handleAction = (actionKey: string) => {
        const baseUrl = `/my/mentorship/programs/${programKey}/modules/${moduleKey}`
        switch (actionKey) {
            case 'edit':
                router.push(`${baseUrl}/edit`)
                break
            case 'issues':
                router.push(`${baseUrl}/issues`)
                break
        }
        setDropdownOpen(false)
    }

    const options = [
        { key: 'edit', label: 'Edit Module' },
        { key: 'issues', label: 'View Issues' },
    ]

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setDropdownOpen(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [])

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                type="button"
                onClick={() => setDropdownOpen((prev) => !prev)}
                className="cursor-pointer rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700"
                aria-label="Module actions menu"
                aria-expanded={dropdownOpen}
                aria-haspopup="true"
            >
                <FontAwesomeIcon
                    className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-200"
                    icon={faEllipsisV}
                />
            </button>
            {dropdownOpen && (
                <div className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
                    {options.map((option) => (
                        <button
                            key={option.key}
                            type="button"
                            role="menuitem"
                            onClick={() => handleAction(option.key)}
                            className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
                        >
                            {option.label}
                        </button>
                    ))}
                </div>
            )}
        </div>
    )
}

export default ModuleActions
