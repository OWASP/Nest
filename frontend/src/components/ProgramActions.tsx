'use client'

import { faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

interface ProgramActionsProps {
  programKey: string
  status: string
  setStatus: (newStatus: string) => void
}

const ProgramActions: React.FC<ProgramActionsProps> = ({ programKey, status, setStatus }) => {
  const router = useRouter()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const handleAction = (actionKey: string) => {
    switch (actionKey) {
      case 'edit Program':
        router.push(`/my/mentorship/programs/${programKey}/edit`)
        break
      case 'create_module':
        router.push(`/my/mentorship/programs/${programKey}/modules/create`)
        break
      case 'publish':
        setStatus(ProgramStatusEnum.Published)
        break
      case 'draft':
        setStatus(ProgramStatusEnum.Draft)
        break
      case 'completed':
        setStatus(ProgramStatusEnum.Completed)
        break
    }
    setDropdownOpen(false)
  }

  const options = [
    { key: 'edit Program', label: 'Edit Program' },
    { key: 'create_module', label: 'Add Module' },
    ...(status === ProgramStatusEnum.Draft ? [{ key: 'publish', label: 'Publish Program' }] : []),
    ...(status === ProgramStatusEnum.Published || status === ProgramStatusEnum.Completed
      ? [{ key: 'draft', label: 'Move to Draft' }]
      : []),
    ...(status === ProgramStatusEnum.Published
      ? [{ key: 'completed', label: 'Mark as Completed' }]
      : []),
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
        data-testid="program-actions-button"
        type="button"
        onClick={() => setDropdownOpen((prev) => !prev)}
        className="rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700"
        aria-label="Program actions menu"
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

export default ProgramActions
