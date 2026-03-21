'use client'

import { Select, SelectItem } from '@heroui/select'
import type React from 'react'
import { cn } from 'utils/utility'

export type MemberFilter = {
  key: string
  label: string
  facetKey: string
  group: string
}

export const AFFINITY_FILTERS: MemberFilter[] = [
  {
    key: 'projects',
    label: 'Projects',
    facetKey: 'idx_has_project_affinity',
    group: 'affinity',
  },
  {
    key: 'chapters',
    label: 'Chapters',
    facetKey: 'idx_has_chapter_affinity',
    group: 'affinity',
  },
  {
    key: 'committees',
    label: 'Committees',
    facetKey: 'idx_has_committee_affinity',
    group: 'affinity',
  },
]

export const ROLE_FILTERS: MemberFilter[] = [
  {
    key: 'staff',
    label: 'OWASP Staff',
    facetKey: 'idx_is_owasp_staff',
    group: 'role',
  },
  {
    key: 'board',
    label: 'Board Member',
    facetKey: 'idx_owasp_board_member',
    group: 'role',
  },
  {
    key: 'gsoc',
    label: 'GSoC Mentor',
    facetKey: 'idx_owasp_gsoc_mentor',
    group: 'role',
  },
]

export const AFFINITY_OPTIONS = [
  { key: 'all', label: 'All Affinity' },
  { key: 'projects', label: 'Projects' },
  { key: 'chapters', label: 'Chapters' },
  { key: 'committees', label: 'Committees' },
]

export const MEMBER_TYPE_OPTIONS = [
  { key: 'all', label: 'All Types' },
  { key: 'staff', label: 'OWASP Staff' },
  { key: 'board', label: 'Board Member' },
  { key: 'gsoc', label: 'GSoC Mentor' },
]

interface MembersFilterProps {
  selectedAffinity: string
  onAffinityChange: (value: string) => void
  selectedMemberTypes: string[]
  onMemberTypesChange: (value: string[]) => void
}

const MembersFilter: React.FC<MembersFilterProps> = ({
  selectedAffinity,
  onAffinityChange,
  selectedMemberTypes,
  onMemberTypesChange,
}) => {
  const selectClassNames = (isActive: boolean) => ({
    trigger:
      'bg-transparent data-[hover=true]:bg-transparent focus:outline-none focus:underline border-none shadow-none text-nowrap w-36 min-h-8 h-8 text-sm font-medium text-gray-800 dark:text-gray-200 hover:text-gray-900 dark:hover:text-gray-100 transition-all duration-0',
    value: cn(
      'text-gray-800 dark:text-gray-200 font-medium',
      isActive && 'text-blue-600 dark:text-blue-400'
    ),
    selectorIcon: 'text-gray-500 dark:text-gray-400 transition-transform duration-200',
    popoverContent:
      'bg-white dark:bg-[#2a2a2a] border border-gray-200 dark:border-gray-600 rounded-md shadow-lg min-w-36 p-1 focus:outline-none',
    listbox: 'p-0 focus:outline-none',
  })

  const combinedOptions = [
    { key: 'all', label: 'All Filters', type: 'all' as const },
    { key: 'projects', label: 'Projects', type: 'affinity' as const },
    { key: 'chapters', label: 'Chapters', type: 'affinity' as const },
    { key: 'committees', label: 'Committees', type: 'affinity' as const },
    { key: 'staff', label: 'OWASP Staff', type: 'role' as const },
    { key: 'board', label: 'Board Member', type: 'role' as const },
    { key: 'gsoc', label: 'GSoC Mentor', type: 'role' as const },
  ]

  const getCurrentKey = () => {
    if (
      selectedAffinity === 'all' &&
      (selectedMemberTypes.length === 0 || selectedMemberTypes.includes('all'))
    ) {
      return 'all'
    }
    if (selectedAffinity === 'all') {
      return selectedMemberTypes[0]
    }
    return selectedAffinity
  }

  const currentKey = getCurrentKey()
  const isActive = currentKey !== 'all'

  const getTestId = (option: (typeof combinedOptions)[number]) => {
    if (option.type === 'affinity') {
      return `affinity-option-${option.key}`
    }
    if (option.type === 'role') {
      return `type-option-${option.key}`
    }
    return 'filter-reset-all'
  }

  const handleChange = (value: string) => {
    if (value === 'all') {
      if (selectedAffinity !== 'all') onAffinityChange('all')
      if (!selectedMemberTypes.includes('all')) onMemberTypesChange(['all'])
      return
    }
    const option = combinedOptions.find((o) => o.key === value)
    if (!option) return
    if (option.type === 'affinity') {
      onAffinityChange(option.key)
      if (!selectedMemberTypes.includes('all')) onMemberTypesChange(['all'])
    }
    if (option.type === 'role') {
      onMemberTypesChange([option.key])
      if (selectedAffinity !== 'all') onAffinityChange('all')
    }
  }

  return (
    <div data-testid="members-filter" className="inline-flex items-center">
      <div
        className={
          'inline-flex h-12 items-center rounded-l-lg rounded-r-none border border-r-0 border-gray-300 bg-white pl-3 shadow-none dark:border-gray-600 dark:bg-gray-800'
        }
      >
        <Select
          selectedKeys={[currentKey]}
          onChange={(e) => handleChange((e.target as HTMLSelectElement).value)}
          classNames={selectClassNames(isActive)}
        >
          {combinedOptions.map((option) => (
            <SelectItem
              key={option.key}
              data-testid={getTestId(option)}
              classNames={{
                base: 'text-sm text-gray-700 dark:text-gray-300 hover:bg-transparent dark:hover:bg-transparent focus:bg-gray-100 dark:focus:bg-[#404040] focus:outline-none rounded-sm px-3 py-2 cursor-pointer data-[selected=true]:bg-blue-50 dark:data-[selected=true]:bg-blue-900/20 data-[selected=true]:text-blue-600 dark:data-[selected=true]:text-blue-400 data-[focus=true]:bg-gray-100 dark:data-[focus=true]:bg-[#404040]',
              }}
            >
              {option.label}
            </SelectItem>
          ))}
        </Select>
      </div>
    </div>
  )
}

export default MembersFilter
