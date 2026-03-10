'use client'

import type { ProjectCategoryOption } from 'hooks/useProjectCategories'
import React, { useState, useRef, useEffect, useId, useCallback } from 'react'
import { FaChevronDown, FaChevronRight } from 'react-icons/fa6'
import { cn } from 'utils/utility'

interface NestedCategorySelectProps {
  categories: ProjectCategoryOption[]
  selected: string
  onSelect: (slug: string) => void
  filterOptions?: Array<{ label: string; key: string }>
}

interface CategoryItemProps {
  slug: string
  name: string
  isSelected: boolean
  hasChildren?: boolean
  onSelect: (slug: string) => void
}

const CategoryItem: React.FC<CategoryItemProps> = ({
  slug,
  name,
  isSelected,
  hasChildren,
  onSelect,
}) => (
  <div
    role="menuitem"
    tabIndex={-1}
    onClick={() => onSelect(slug)}
    onKeyDown={(e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onSelect(slug)
      }
    }}
    className={cn(
      'flex cursor-pointer items-center justify-between px-3 py-2 text-sm transition-colors',
      isSelected
        ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
        : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-[#404040]'
    )}
  >
    {name}
    {hasChildren && <FaChevronRight className="h-3 w-3 text-gray-400 dark:text-gray-500" />}
  </div>
)

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

  const handleSelect = useCallback(
    (slug: string) => {
      onSelect(slug)
      setIsOpen(false)
    },
    [onSelect]
  )

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false)
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setIsOpen((prev) => !prev)
    }
  }

  const topLevel = categories.filter((cat) => cat.level === 1)

  const getCategoryChildren = useCallback(
    (categoryName: string, level: number) => {
      return categories.filter((cat) => {
        if (cat.level !== level + 1) return false
        const parts = cat.fullPath.split(' -> ')
        return parts.length === level + 1 && parts[level - 1] === categoryName
      })
    },
    [categories]
  )

  const getSelectedLabel = () => {
    if (!selected) return 'All Categories'
    return (
      filterOptions.find((o) => o.key === selected)?.label ||
      categories.find((c) => c.slug === selected)?.name ||
      'Select'
    )
  }

  const renderLevel3Children = (level2Name: string) => {
    const level3Children = getCategoryChildren(level2Name, 2)
    if (level3Children.length === 0) return null

    return (
      <div className="absolute top-0 left-full z-50 ml-0 hidden w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg group-hover/child:block dark:border-gray-600 dark:bg-[#2a2a2a]">
        {level3Children.map((level3Cat) => (
          <CategoryItem
            key={level3Cat.id}
            slug={level3Cat.slug}
            name={level3Cat.name}
            isSelected={selected === level3Cat.slug}
            onSelect={handleSelect}
          />
        ))}
      </div>
    )
  }

  const renderLevel2Children = (categoryName: string) => {
    const level2Children = getCategoryChildren(categoryName, 1)
    if (level2Children.length === 0) return null

    return (
      <div className="absolute top-0 left-full z-50 ml-0 hidden w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg group-hover/parent:block dark:border-gray-600 dark:bg-[#2a2a2a]">
        {level2Children.map((level2Cat) => {
          const hasLevel3 = getCategoryChildren(level2Cat.name, 2).length > 0

          return (
            <div key={level2Cat.id} className="group/child relative">
              <CategoryItem
                slug={level2Cat.slug}
                name={level2Cat.name}
                isSelected={selected === level2Cat.slug}
                hasChildren={hasLevel3}
                onSelect={handleSelect}
              />
              {hasLevel3 && renderLevel3Children(level2Cat.name)}
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <div className="inline-flex h-12 items-center rounded-lg border border-gray-300 bg-gray-100 pl-3 shadow-sm transition-all duration-200 hover:shadow-md dark:border-gray-600 dark:bg-[#323232]">
        <span className="w-auto pe-3 text-sm font-medium text-gray-700 select-none dark:text-gray-300">
          Filter:
        </span>

        <div className="relative">
          <button
            onClick={() => setIsOpen(!isOpen)}
            onKeyDown={handleKeyDown}
            aria-expanded={isOpen}
            aria-haspopup="menu"
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
              role="menu"
              aria-orientation="vertical"
              className="absolute left-0 z-50 mt-0 w-56 rounded-md border border-gray-200 bg-white py-1 shadow-lg dark:border-gray-600 dark:bg-[#2a2a2a]"
            >
              {/* All Categories option */}
              <CategoryItem
                slug=""
                name="All Categories"
                isSelected={selected === ''}
                onSelect={handleSelect}
              />

              {/* Project categories (nested) */}
              {topLevel.map((category) => {
                const hasChildren = getCategoryChildren(category.name, 1).length > 0

                return (
                  <div key={category.id} className="group/parent relative">
                    <CategoryItem
                      slug={category.slug}
                      name={category.name}
                      isSelected={selected === category.slug}
                      hasChildren={hasChildren}
                      onSelect={handleSelect}
                    />
                    {hasChildren && renderLevel2Children(category.name)}
                  </div>
                )
              })}

              {/* Divider between project categories and filters */}
              {filterOptions.length > 0 && topLevel.length > 0 && (
                <div className="my-1 border-t border-gray-200 dark:border-gray-600" />
              )}

              {/* Filter options (Health, Level, etc.) */}
              {filterOptions
                .filter((option) => option.key !== '')
                .map((option) => (
                  <CategoryItem
                    key={option.key}
                    slug={option.key}
                    name={option.label}
                    isSelected={selected === option.key}
                    onSelect={handleSelect}
                  />
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default NestedCategorySelect
