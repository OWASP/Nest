'use client'

import { faEllipsisV } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { ProgramStatusEnum } from 'types/__generated__/graphql'

interface ProgramActionsProps {
  status: string
  setStatus: (
    newStatus: ProgramStatusEnum.Draft | ProgramStatusEnum.Published | ProgramStatusEnum.Completed
  ) => void
}

const ProgramActions: React.FC<ProgramActionsProps> = ({ status, setStatus }) => {
  const router = useRouter()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<HTMLButtonElement | null>(null)
  const handleAction = (actionKey: string) => {
    switch (actionKey) {
      case 'edit Program':
        router.push(`${globalThis.location.pathname}/edit`)
        break
      case 'create_module':
        router.push(`${globalThis.location.pathname}/modules/create`)
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

  useEffect(() => {
    if (!dropdownOpen) return
    requestAnimationFrame(() => {
      const items = dropdownRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]')
      if (items && items.length > 0) items[0].focus()
    })
  }, [dropdownOpen])

  const handleMenuKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const items = dropdownRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]')
    if (!items || items.length === 0) return

    const current = Array.from(items).indexOf(document.activeElement as HTMLElement)
    switch (e.key) {
      case 'ArrowDown': {
        e.preventDefault()
        const next = current < items.length - 1 ? current + 1 : 0
        items[next].focus()
        break
      }
      case 'ArrowUp': {
        e.preventDefault()
        const prev = current > 0 ? current - 1 : items.length - 1
        items[prev].focus()
        break
      }
      case 'Home': {
        e.preventDefault()
        items[0].focus()
        break
      }
      case 'End': {
        e.preventDefault()
        items[items.length - 1].focus()
        break
      }
      case 'Escape': {
        e.preventDefault()
        setDropdownOpen(false)
        triggerRef.current?.focus()
        break
      }
      default:
        break
    }
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        data-testid="program-actions-button"
        type="button"
        aria-haspopup="menu"
        aria-expanded={dropdownOpen}
        onClick={() => setDropdownOpen((prev) => !prev)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            setDropdownOpen((prev) => !prev)
          }
        }}
        className="rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700 focus:outline-none focus-visible:ring-1 focus-visible:ring-offset-1"
      >
        <FontAwesomeIcon icon={faEllipsisV} />
      </button>
      {dropdownOpen && (
        <div
          role="menu"
          onKeyDown={handleMenuKeyDown}
          className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
        >
          {options.map((option) => (
            <button
              key={option.key}
              type="button"
              role="menuitem"
              onClick={() => handleAction(option.key)}
              className="block w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus-visible:ring-1 focus-visible:ring-offset-1"
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
