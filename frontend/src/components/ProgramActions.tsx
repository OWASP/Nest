'use client'

import { useRouter } from 'next/navigation'
import React, { useState, useRef, useEffect } from 'react'

interface ProgramActionsProps {
  status: string
  setStatus: (newStatus: 'DRAFT' | 'PUBLISHED' | 'COMPLETED') => void
}

const ProgramActions: React.FC<ProgramActionsProps> = ({ status, setStatus }) => {
  const router = useRouter()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const handleAction = (actionKey: string) => {
    switch (actionKey) {
      case 'create_module':
        router.push(`${window.location.pathname}/modules/create`)
        break
      case 'publish':
        setStatus('PUBLISHED')
        break
      case 'draft':
        setStatus('DRAFT')
        break
      case 'completed':
        setStatus('COMPLETED')
        break
    }
    setIsOpen(false)
  }

  const options = [
    { key: 'create_module', label: 'Add Module' },
    ...(status === 'DRAFT' ? [{ key: 'publish', label: 'Publish Program' }] : []),
    ...(status === 'PUBLISHED' || status === 'COMPLETED'
      ? [{ key: 'draft', label: 'Move to Draft' }]
      : []),
    ...(status === 'PUBLISHED' ? [{ key: 'completed', label: 'Mark as Completed' }] : []),
  ]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="flex items-center gap-2">
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen((prev) => !prev)}
          className="w-full rounded-lg border-b border-gray-100 bg-[#D1DBE6] px-4 py-3 text-left text-sm text-gray-700 transition-colors last:border-b-0 dark:border-gray-600 dark:bg-[#454545] dark:text-gray-300"
        >
          Select Action
          <svg
            className={`ml-2 inline h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute left-0 top-full z-50 mt-1 w-full min-w-[8rem] overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-600 dark:bg-[#323232]">
            {options.map((option) => (
              <button
                key={option.key}
                type="button"
                role="menuitem"
                onClick={() => handleAction(option.key)}
                className="w-full border-b border-gray-100 px-3 py-2 text-left text-sm text-gray-700 transition-colors last:border-b-0 hover:bg-[#D1DBE6] dark:border-gray-600 dark:text-gray-300 dark:hover:bg-[#454545]"
              >
                {option.label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default ProgramActions
