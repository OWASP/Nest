'use client'

import { useQuery } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import { useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { FaCircleExclamation } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
import { handleAppError } from 'app/global-error'
import { GetManagementModuleIssuesDocument } from 'types/__generated__/moduleQueries.generated'
import { DEADLINE_ALL, DEADLINE_OPTIONS, getDeadlineCategory } from 'utils/deadlineUtils'
import { isForbiddenGraphQLError } from 'utils/helpers/handleGraphQLError'
import AnchorTitle from 'components/AnchorTitle'
import IssuesTable from 'components/IssuesTable'
import Pagination from 'components/Pagination'
import SecondaryCard from 'components/SecondaryCard'

const ITEMS_PER_PAGE = 10
const LABEL_ALL = 'all'
const MAX_ISSUES_FOR_DEADLINE_FILTER = 1000

interface ModuleIssuesProps {
  programKey: string
  moduleKey: string
}

const ModuleIssues = ({ programKey, moduleKey }: ModuleIssuesProps) => {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedLabel, setSelectedLabel] = useState<string>(searchParams.get('label') || LABEL_ALL)
  const [selectedDeadline, setSelectedDeadline] = useState<string>(
    searchParams.get('deadline') || DEADLINE_ALL
  )
  const [currentPage, setCurrentPage] = useState(1)

  const isDeadlineFilterActive = selectedDeadline !== DEADLINE_ALL

  // A single role-aware query serves admins, mentors, and mentees.
  const { data, loading, error } = useQuery(GetManagementModuleIssuesDocument, {
    variables: {
      programKey,
      moduleKey,
      limit: isDeadlineFilterActive ? MAX_ISSUES_FOR_DEADLINE_FILTER : ITEMS_PER_PAGE,
      offset: isDeadlineFilterActive ? 0 : (currentPage - 1) * ITEMS_PER_PAGE,
      label: selectedLabel === LABEL_ALL ? null : selectedLabel,
    },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (error && !isForbiddenGraphQLError(error)) {
      handleAppError(error)
    }
  }, [error])

  const moduleData = data?.managementModule
  const isMentee = moduleData?.userRole === 'mentee'

  // Mentees have no filter controls, so a filtered URL (shared link, history, manual
  // edit) would trap them on a filtered/empty list with no way to clear it. Once we
  // know the caller is a mentee, drop any active filters and strip the URL params.
  useEffect(() => {
    if (isMentee && (selectedLabel !== LABEL_ALL || selectedDeadline !== DEADLINE_ALL)) {
      setSelectedLabel(LABEL_ALL)
      setSelectedDeadline(DEADLINE_ALL)
      setCurrentPage(1)
      const params = new URLSearchParams(searchParams.toString())
      params.delete('label')
      params.delete('deadline')
      const qs = params.toString()
      router.replace(qs ? `?${qs}` : globalThis.location.pathname, { scroll: false })
    }
  }, [isMentee, selectedLabel, selectedDeadline, searchParams, router])

  const { moduleIssues, filteredCount } = useMemo(() => {
    const allIssues = (moduleData?.issues || []).map((i) => ({
      objectID: i.id,
      number: i.number,
      title: i.title,
      state: i.state,
      isMerged: i.isMerged,
      labels: i.labels || [],
      assignees: i.assignees || [],
      deadline: i.taskDeadline ?? null,
    }))

    if (selectedDeadline !== DEADLINE_ALL) {
      // Filter by deadline category
      const filtered = allIssues.filter(
        (issue) => getDeadlineCategory(issue.deadline) === selectedDeadline
      )
      // Apply client-side pagination on filtered results
      const start = (currentPage - 1) * ITEMS_PER_PAGE
      const paginatedIssues = filtered.slice(start, start + ITEMS_PER_PAGE)
      return { moduleIssues: paginatedIssues, filteredCount: filtered.length }
    }

    return { moduleIssues: allIssues, filteredCount: moduleData?.issuesCount || 0 }
  }, [moduleData, selectedDeadline, currentPage])

  const totalPages = Math.ceil(
    (isDeadlineFilterActive ? filteredCount : moduleData?.issuesCount || 0) / ITEMS_PER_PAGE
  )

  const allLabels: string[] = useMemo(() => {
    const serverLabels = moduleData?.availableLabels
    if (serverLabels && serverLabels.length > 0) {
      return serverLabels
    }

    const labels = new Set<string>()
    ;(moduleData?.issues || []).forEach((i) =>
      (i.labels || []).forEach((l: string) => labels.add(l))
    )
    return Array.from(labels).sort((a, b) => a.localeCompare(b))
  }, [moduleData])

  const applyFilter = (name: string, value: string, clearedValue: string) => {
    setCurrentPage(1)
    const params = new URLSearchParams(searchParams.toString())
    if (value === clearedValue) {
      params.delete(name)
    } else {
      params.set(name, value)
    }
    const qs = params.toString()
    router.replace(qs ? `?${qs}` : globalThis.location.pathname, { scroll: false })
  }

  const handleLabelChange = (label: string) => {
    setSelectedLabel(label)
    applyFilter('label', label, LABEL_ALL)
  }

  const handleDeadlineChange = (deadline: string) => {
    setSelectedDeadline(deadline)
    applyFilter('deadline', deadline, DEADLINE_ALL)
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const handleIssueClick = useCallback(
    (issueNumber: number) => {
      router.push(
        `/my/mentorship/programs/${programKey}/modules/${moduleKey}/issues/${issueNumber}`
      )
    },
    [router, programKey, moduleKey]
  )

  if (error && isForbiddenGraphQLError(error)) {
    return null
  }

  const isInitialLoad = loading && !moduleData

  return (
    <SecondaryCard>
      <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="flex flex-row items-center gap-2 text-2xl font-semibold">
          <IconWrapper icon={FaCircleExclamation} className="h-5 w-5" />
          <AnchorTitle title="Issues" />
        </h2>

        {/* Filters are a management affordance; mentees get a plain list of their issues. */}
        {!isMentee && (
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            <div className="flex h-12 w-full items-center overflow-hidden rounded-lg bg-gray-200 sm:w-auto dark:bg-[#323232]">
              <Select
                labelPlacement="outside-left"
                size="md"
                aria-label="Filter by label"
                label="Label :"
                classNames={{
                  label:
                    'font-small text-sm text-gray-600 hover:cursor-pointer dark:text-gray-300 pl-[1.4rem] w-auto',
                  trigger:
                    'bg-transparent shadow-none pl-0 text-nowrap rounded-none w-full sm:w-40',
                  selectorIcon: 'right-3',
                  popoverContent: 'text-md min-w-40 dark:bg-[#323232] rounded-none p-0',
                }}
                selectedKeys={new Set([selectedLabel])}
                onSelectionChange={(keys) => {
                  const [key] = Array.from(keys as Set<string>)
                  if (key !== undefined) handleLabelChange(key)
                }}
              >
                {[LABEL_ALL, ...allLabels].map((l) => (
                  <SelectItem
                    key={l}
                    classNames={{
                      base: 'text-sm hover:bg-[#D1DBE6] dark:hover:bg-[#454545] rounded-none px-3 py-0.5',
                    }}
                  >
                    {l === LABEL_ALL ? 'All' : l}
                  </SelectItem>
                ))}
              </Select>
            </div>
            <div className="flex h-12 w-full items-center overflow-hidden rounded-lg bg-gray-200 sm:w-auto dark:bg-[#323232]">
              <Select
                labelPlacement="outside-left"
                size="md"
                aria-label="Filter by deadline"
                label="Deadline :"
                classNames={{
                  label:
                    'font-small text-sm text-gray-600 hover:cursor-pointer dark:text-gray-300 pl-[1.4rem] w-auto',
                  trigger:
                    'bg-transparent pl-0 shadow-none text-nowrap rounded-none w-full sm:w-36',
                  selectorIcon: 'right-3',
                  popoverContent: 'text-md min-w-36 dark:bg-[#323232] rounded-none p-0',
                }}
                selectedKeys={new Set([selectedDeadline])}
                onSelectionChange={(keys) => {
                  const [key] = Array.from(keys as Set<string>)
                  if (key) handleDeadlineChange(key)
                }}
              >
                {DEADLINE_OPTIONS.map((option) => (
                  <SelectItem
                    key={option.key}
                    classNames={{
                      base: 'text-sm hover:bg-[#D1DBE6] dark:hover:bg-[#454545] rounded-none px-3 py-0.5',
                    }}
                  >
                    {option.label}
                  </SelectItem>
                ))}
              </Select>
            </div>
          </div>
        )}
      </div>

      <IssuesTable
        issues={moduleIssues}
        showAssignee={true}
        showDeadline={true}
        onIssueClick={handleIssueClick}
        emptyMessage={
          isInitialLoad ? 'Loading issues...' : 'No issues found for the selected filter.'
        }
      />

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          isLoaded={!loading}
        />
      )}
    </SecondaryCard>
  )
}

export default ModuleIssues
