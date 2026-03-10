'use client'

import React, { useState, useRef, useEffect, useId } from 'react'
import { FaChevronDown, FaChevronRight } from 'react-icons/fa6'
import type { ProjectCategoryOption } from 'hooks/useProjectCategories'
import { cn } from 'utils/utility'

interface NestedCategorySelectProps {
  categories: ProjectCategoryOption[]
  selected: string
  onSelect: (slug: string) => void
  filterOptions?: Array<{ label: string; key: string }>
}

const NestedCategorySelect: React.FC<NestedCategorySelectProps> = ({
  categories,
  selected,
  onSelect,
  filterOptions = [],
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const dropdownId = useId()

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (slug: string) => {
    onSelect(slug)
    setIsOpen(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false)
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setIsOpen((prev) => !prev)
    }
  }

  const topLevel = categories.filter((cat) => cat.level === 1)

  const getCategoryChildren = (categoryName: string, level: number) => {
    return categories.filter((cat) => {
      if (cat.level !== level + 1) return false
      const parts = cat.full_path.split(' -> ')
      return parts.length === level + 1 && parts[level - 1] === categoryName
    })
  }

  const getSelectedLabel = () => {
    if (!selected) return 'All Categories'
    return (
      filterOptions.find((o) => o.key === selected)?.label ||
      categories.find((c) => c.slug === selected)?.name ||
      'Select'
    )
  }

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
        <label className="w-auto select-none pe-3 text-sm font-medium text-gray-700 dark:text-gray-300">
          Filter:
        </label>

        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            onKeyDown={handleKeyDown}
            aria-expanded={isOpen}
            aria-haspopup="listbox"
            aria-controls={dropdownId}
            className="flex h-8 min-h-8 items-center bg-transparent px-3 py-2 text-sm font-medium text-nowrap text-gray-800 transition-all duration-200 hover:text-gray-900 focus:outline-none dark:text-gray-200 dark:hover:text-gray-100"
          >
            {getSelectedLabel()}
            <FaChevronDown
              className={cn(
                'ml-2 h-3 w-3 text-gray-500 transition-transform duration-200 dark:text-gray-400',
                isOpen && 'rotate-180'
              )}
            />
          </button>

          {isOpen && (
            <div
              id={dropdownId}
              role="listbox"
              className="absolute left-0 z-50 mt-0 w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-600 dark:bg-[#2a2a2a]"
            >
              {/* All Categories option */}
              <div
                role="option"
                aria-selected={selected === ''}
                onClick={() => handleSelect('')}
                className={cn(
                  'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
                  selected === ''
                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
                )}
              >
                All Categories
              </div>

              {/* Project categories (nested) */}
              {topLevel.map((category) => {
                const level2Children = getCategoryChildren(category.name, 1)
                const hasChildren = level2Children.length > 0

                return (
                  <div key={category.id} className="group/parent relative">
                    <div
                      role="option"
                      aria-selected={selected === category.slug}
                      onClick={() => handleSelect(category.slug)}
                      className={cn(
                        'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
                        selected === category.slug
                          ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
                      )}
                    >
                      {category.name}
                      {hasChildren && (
                        <FaChevronRight className="h-3 w-3 text-gray-400 dark:text-gray-500" />
                      )}
                    </div>

                    {/* Level 2 submenu */}
                    {hasChildren && (
                      <div className="absolute left-full top-0 z-50 ml-0 hidden w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg group-hover/parent:block dark:border-gray-600 dark:bg-[#2a2a2a]">
                        {level2Children.map((level2Cat) => {
                          const level3Children = getCategoryChildren(level2Cat.name, 2)
                          const hasLevel3 = level3Children.length > 0

                          return (
                            <div key={level2Cat.id} className="group/child relative">
                              <div
                                role="option"
                                aria-selected={selected === level2Cat.slug}
                                onClick={() => handleSelect(level2Cat.slug)}
                                className={cn(
                                  'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
                                  selected === level2Cat.slug
                                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
                                )}
                              >
                                {level2Cat.name}
                                {hasLevel3 && (
                                  <FaChevronRight className="h-3 w-3 text-gray-400 dark:text-gray-500" />
                                )}
                              </div>

                              {/* Level 3 submenu */}
                              {hasLevel3 && (
                                <div className="absolute left-full top-0 z-50 ml-0 hidden w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg group-hover/child:block dark:border-gray-600 dark:bg-[#2a2a2a]">
                                  {level3Children.map((level3Cat) => (
                                    <div
                                      key={level3Cat.id}
                                      role="option"
                                      aria-selected={selected === level3Cat.slug}
                                      onClick={() => handleSelect(level3Cat.slug)}
                                      className={cn(
                                        'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
                                        selected === level3Cat.slug
                                          ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                          : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
                                      )}
                                    >
                                      {level3Cat.name}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              })}

              {/* Divider between project categories and filters */}
              {filterOptions.length > 0 && topLevel.length > 0 && (
                <div className="my-1 border-t border-gray-200 dark:border-gray-600" />
              )}

              {/* Filter options (Health, Level, etc.) */}
              {filterOptions.map((option) => (
                <div
                  key={option.key}
                  role="option"
                  aria-selected={selected === option.key}
                  onClick={() => handleSelect(option.key)}
                  className={cn(
                    'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
                    selected === option.key
                      ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
                  )}
                >
                  {option.label}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default NestedCategorySelect
