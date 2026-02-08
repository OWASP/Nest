'use client'

import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { FaEllipsisV } from 'react-icons/fa'
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
  const [focusIndex, setFocusIndex] = useState(-1)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerButtonRef = useRef<HTMLButtonElement>(null)
  const menuItemsRef = useRef<(HTMLButtonElement | null)[]>([])

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
        setFocusIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  useEffect(() => {
    if (focusIndex >= 0 && menuItemsRef.current[focusIndex]) {
      menuItemsRef.current[focusIndex]?.focus()
    }
  }, [focusIndex])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!dropdownOpen) return

    const optionsCount = options.length

    switch (e.key) {
      case 'Escape':
        e.preventDefault()
        setDropdownOpen(false)
        setFocusIndex(-1)
        triggerButtonRef.current?.focus()
        break
      case 'ArrowDown':
        e.preventDefault()
        setFocusIndex((prev) => (prev < optionsCount - 1 ? prev + 1 : 0))
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusIndex((prev) => (prev > 0 ? prev - 1 : optionsCount - 1))
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        if (focusIndex >= 0) {
          menuItemsRef.current[focusIndex]?.click()
        }
        break
      default:
        break
    }
  }

  const handleToggle = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const newState = !dropdownOpen
    setDropdownOpen(newState)
    if (newState) {
      setFocusIndex(0)
    } else {
      setFocusIndex(-1)
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        ref={triggerButtonRef}
        type="button"
        onClick={handleToggle}
        className="cursor-pointer rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700"
        aria-label={`${type === 'program' ? 'Program' : 'Module'} actions menu`}
        aria-expanded={dropdownOpen}
        aria-haspopup="true"
      >
        <FaEllipsisV className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-200" />
      </button>
      {dropdownOpen && (
        <div
          className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
          onKeyDown={handleKeyDown}
          role="menu"
          tabIndex={dropdownOpen ? 0 : -1}
        >
          {options.map((option, index) => {
            const handleMenuItemClick = (e: React.MouseEvent) => {
              e.preventDefault()
              e.stopPropagation()
              handleAction(option.key)
              setFocusIndex(-1)
            }

            return (
              <button
                key={option.key}
                ref={(el) => {
                  menuItemsRef.current[index] = el
                }}
                type="button"
                role="menuitem"
                tabIndex={focusIndex === index ? 0 : -1}
                onClick={handleMenuItemClick}
                className="block w-full cursor-pointer px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
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
