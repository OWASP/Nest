'use client'

import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { FaEllipsisV } from 'react-icons/fa'

interface ActionItem {
  className?: string
  key: string
  label: string
  onAction: () => void
}

interface DropdownActionsProps {
  label?: string
  options: ActionItem[]
}

const DropdownActions: React.FC<DropdownActionsProps> = ({ options, label }) => {
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [focusIndex, setFocusIndex] = useState(-1)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerButtonRef = useRef<HTMLButtonElement>(null)
  const menuItemsRef = useRef<(HTMLButtonElement | null)[]>([])

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

  if (options.length === 0) return null

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
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
        menuItemsRef.current[focusIndex]?.click()
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
        aria-label={label ?? 'Actions menu'}
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
          tabIndex={-1}
        >
          {options.map((option, index) => {
            const handleMenuItemClick = (e: React.MouseEvent) => {
              e.preventDefault()
              e.stopPropagation()
              option.onAction()
              setFocusIndex(-1)
              setDropdownOpen(false)
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
                className={`block w-full cursor-pointer px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 ${
                  option.className || ''
                }`}
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

export default DropdownActions
