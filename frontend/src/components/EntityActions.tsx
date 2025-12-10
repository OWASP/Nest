'use client'

import { faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

interface EntityActionsProps {
  type: 'program' | 'module'
  programKey: string
  moduleKey?: string
  status?: string
  setStatus?: (newStatus: string) => void
}

const EntityActions: React.FC<EntityActionsProps> = ({
  type,
  programKey,
  moduleKey,
  status,
  setStatus,
}) => {
  const router = useRouter()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const [focusedIndex, setFocusedIndex] = useState<number>(-1)
  const menuItemsRef = useRef<(HTMLButtonElement | null)[]>([])
  const triggerButtonRef = useRef<HTMLButtonElement>(null)

  const handleAction = (actionKey: string) => {
    switch (actionKey) {
      case 'edit_program':
        router.push(`/my/mentorship/programs/${programKey}/edit`)
        break
      case 'create_module':
        router.push(`/my/mentorship/programs/${programKey}/modules/create`)
        break
      case 'edit_module':
        if (moduleKey) {
          router.push(`/my/mentorship/programs/${programKey}/modules/${moduleKey}/edit`)
        }
        break
      case 'view_issues':
        if (moduleKey) {
          router.push(`/my/mentorship/programs/${programKey}/modules/${moduleKey}/issues`)
        }
        break
      case 'publish':
        setStatus?.(ProgramStatusEnum.Published)
        break
      case 'draft':
        setStatus?.(ProgramStatusEnum.Draft)
        break
      case 'completed':
        setStatus?.(ProgramStatusEnum.Completed)
        break
    }
    setDropdownOpen(false)
  }

  const options =
    type === 'program'
      ? [
          { key: 'edit_program', label: 'Edit' },
          { key: 'create_module', label: 'Add Module' },
          ...(status === ProgramStatusEnum.Draft ? [{ key: 'publish', label: 'Publish' }] : []),
          ...(status === ProgramStatusEnum.Published || status === ProgramStatusEnum.Completed
            ? [{ key: 'draft', label: 'Unpublish' }]
            : []),
          ...(status === ProgramStatusEnum.Published
            ? [{ key: 'completed', label: 'Mark as Completed' }]
            : []),
        ]
      : [
          { key: 'edit_module', label: 'Edit' },
          { key: 'view_issues', label: 'View Issues' },
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

  useEffect(() => {
    if (dropdownOpen) {
      setFocusedIndex(0)
    } else {
      setFocusedIndex(-1)
      menuItemsRef.current = []
    }
  }, [dropdownOpen])

  useEffect(() => {
    if (dropdownOpen && focusedIndex >= 0 && menuItemsRef.current[focusedIndex]) {
      menuItemsRef.current[focusedIndex]?.focus()
    }
  }, [dropdownOpen, focusedIndex])

  useEffect(() => {
    if (!dropdownOpen && triggerButtonRef.current) {
      triggerButtonRef.current.focus()
    }
  }, [dropdownOpen])

  const handleToggle = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDropdownOpen((prev) => !prev)
  }

  const handleTriggerKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setDropdownOpen((prev) => !prev)
    } else if (e.key === 'Escape' && dropdownOpen) {
      e.preventDefault()
      setDropdownOpen(false)
    } else if (e.key === 'ArrowDown' && !dropdownOpen) {
      e.preventDefault()
      setDropdownOpen(true)
    }
  }

  const handleMenuKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setFocusedIndex((prev) => (prev < options.length - 1 ? prev + 1 : prev))
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusedIndex((prev) => (prev > 0 ? prev - 1 : 0))
        break
      case 'Home':
        e.preventDefault()
        setFocusedIndex(0)
        break
      case 'End':
        e.preventDefault()
        setFocusedIndex(options.length - 1)
        break
      case 'Escape':
        e.preventDefault()
        setDropdownOpen(false)
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        if (focusedIndex >= 0) {
          handleAction(options[focusedIndex].key)
        }
        break
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        ref={triggerButtonRef}
        data-testid={`${type}-actions-button`}
        type="button"
        onClick={handleToggle}
        onKeyDown={handleTriggerKeyDown}
        className="cursor-pointer rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:outline-hidden dark:focus:ring-blue-300"
        aria-label={`${type === 'program' ? 'Program' : 'Module'} actions menu`}
        aria-expanded={dropdownOpen}
        aria-haspopup="true"
      >
        <FontAwesomeIcon
          className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-200"
          icon={faEllipsisV}
        />
      </button>
      {dropdownOpen && (
        <div
          role="menu"
          className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
        >
          {options.map((option, index) => {
            const handleMenuItemClick = (e: React.MouseEvent) => {
              e.preventDefault()
              e.stopPropagation()
              handleAction(option.key)
            }

            return (
              <button
                key={option.key}
                ref={(el) => (menuItemsRef.current[index] = el)}
                type="button"
                role="menuitem"
                tabIndex={-1}
                onClick={handleMenuItemClick}
                onKeyDown={handleMenuKeyDown}
                className="block w-full cursor-pointer px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 focus:bg-gray-100 focus:outline-none dark:focus:bg-gray-700"
              >
                {option.label}
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default EntityActions
