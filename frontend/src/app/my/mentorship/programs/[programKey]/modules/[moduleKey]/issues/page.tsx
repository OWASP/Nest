'use client'

import { useQuery } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { useAccessControl } from 'hooks/useAccessControl'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import {
  GetManagementModuleIssuesDocument,
  GetManagementProgramAdminsAndModulesDocument,
  GetModuleIssuesDocument,
} from 'types/__generated__/moduleQueries.generated'
import { hasExtendedUser } from 'types/auth'
import type { ExtendedSession } from 'types/auth'
import { DEADLINE_ALL, DEADLINE_OPTIONS, getDeadlineCategory } from 'utils/deadlineUtils'
import { isForbiddenGraphQLError } from 'utils/helpers/handleGraphQLError'
import AccessDeniedDisplay from 'components/AccessDeniedDisplay'
import IssuesTable from 'components/IssuesTable'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'

const ITEMS_PER_PAGE = 20
const LABEL_ALL = 'all'

const IssuesPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { data: session, status: sessionStatus } = useSession() as {
    data: ExtendedSession | null
    status: string
  }
  const currentUserLogin = session?.user?.login
  const isProjectLeader = hasExtendedUser(session) ? session.user.isLeader : false
  const isMentor = hasExtendedUser(session) ? session.user.isMentor : false
  const isMenteeUser = !isProjectLeader && !isMentor

  const [selectedLabel, setSelectedLabel] = useState<string>(searchParams.get('label') || LABEL_ALL)
  const [selectedDeadline, setSelectedDeadline] = useState<string>(
    searchParams.get('deadline') || DEADLINE_ALL
  )
  const [currentPage, setCurrentPage] = useState(1)

  const isDeadlineFilterActive = selectedDeadline !== DEADLINE_ALL
  const MAX_ISSUES_FOR_DEADLINE_FILTER = 1000

  const {
    data: accessData,
    loading: accessLoading,
    error: accessError,
  } = useQuery(GetManagementProgramAdminsAndModulesDocument, {
    variables: { programKey, moduleKey },
    skip: !programKey || !moduleKey || isMenteeUser,
    fetchPolicy: 'network-only',
  })

  const hasAccess = useAccessControl(accessData, sessionStatus, currentUserLogin, accessLoading)

  useEffect(() => {
    if (accessError && !isForbiddenGraphQLError(accessError)) {
      handleAppError(accessError)
    }
  }, [accessError])

  const { data, loading, error } = useQuery(GetManagementModuleIssuesDocument, {
    variables: {
      programKey,
      moduleKey,
      limit: isDeadlineFilterActive ? MAX_ISSUES_FOR_DEADLINE_FILTER : ITEMS_PER_PAGE,
      offset: isDeadlineFilterActive ? 0 : (currentPage - 1) * ITEMS_PER_PAGE,
      label: selectedLabel === LABEL_ALL ? null : selectedLabel,
    },
    skip: !programKey || !moduleKey || !hasAccess || isMenteeUser,
    fetchPolicy: 'cache-and-network',
  })

  const {
    data: menteeIssuesData,
    loading: menteeIssuesLoading,
    error: menteeIssuesError,
  } = useQuery(GetModuleIssuesDocument, {
    variables: {
      programKey,
      moduleKey,
      limit: isDeadlineFilterActive ? MAX_ISSUES_FOR_DEADLINE_FILTER : ITEMS_PER_PAGE,
      offset: isDeadlineFilterActive ? 0 : (currentPage - 1) * ITEMS_PER_PAGE,
      label: selectedLabel === LABEL_ALL ? null : selectedLabel,
    },
    skip: !programKey || !moduleKey || !isMenteeUser,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (error && !isForbiddenGraphQLError(error)) {
      handleAppError(error)
    }
  }, [error])

  const moduleData = data?.managementModule

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

  const handleLabelChange = (label: string) => {
    setSelectedLabel(label)
    setCurrentPage(1)
    const params = new URLSearchParams(searchParams.toString())
    if (label === LABEL_ALL) {
      params.delete('label')
    } else {
      params.set('label', label)
    }
    router.replace(`?${params.toString()}`)
  }

  const handleDeadlineChange = (deadline: string) => {
    setSelectedDeadline(deadline)
    setCurrentPage(1)
    const params = new URLSearchParams(searchParams.toString())
    if (deadline === DEADLINE_ALL) {
      params.delete('deadline')
    } else {
      params.set('deadline', deadline)
    }
    router.replace(`?${params.toString()}`)
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

  if (isMenteeUser) {
    if (menteeIssuesLoading) return <LoadingSpinner />

    const menteeModuleData = menteeIssuesData?.getModule
    const menteeIssues = (menteeModuleData?.issues || []).map((i) => ({
      objectID: i.id,
      number: i.number,
      title: i.title,
      state: i.state,
      isMerged: i.isMerged,
      labels: i.labels || [],
      assignees: i.assignees || [],
      deadline: i.taskDeadline ?? null,
    }))

    const menteeTotalPages = Math.ceil((menteeModuleData?.issuesCount || 0) / ITEMS_PER_PAGE)

    return (
      <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
        <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
          <div className="mx-auto max-w-6xl">
            <h1 className="mb-6 text-2xl font-bold sm:text-3xl">
              {menteeModuleData?.name} — My Issues
            </h1>
            <IssuesTable
              issues={menteeIssues}
              onIssueClick={handleIssueClick}
              currentUserLogin={currentUserLogin}
            />
            {menteeTotalPages > 1 && (
              <Pagination
                total={menteeTotalPages}
                initialPage={currentPage}
                onChange={handlePageChange}
              />
            )}
          </div>
        </div>
      </BreadcrumbStyleProvider>
    )
  }

  if (sessionStatus === 'loading' || accessLoading || hasAccess === undefined) {
    return <LoadingSpinner />
  }

  if (accessError && isForbiddenGraphQLError(accessError)) {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to manage issues for this module."
      />
    )
  }

  if (accessError) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Error Loading Access Information"
        message="Failed to verify access permissions. Please try again later."
      />
    )
  }

  if (!hasAccess) {
    return (
      <AccessDeniedDisplay
        title="Access Denied"
        message="Only program admins and module mentors can access this page."
      />
    )
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error && isForbiddenGraphQLError(error)) {
    return (
      <ErrorDisplay
        statusCode={403}
        title="Access Denied"
        message="You do not have permission to view issues for this module."
      />
    )
  }

  if (error) {
    return (
      <ErrorDisplay
        statusCode={500}
        title="Server Error"
        message="Failed to load issues for this module. Please try again later."
      />
    )
  }

  if (!moduleData)
    return <ErrorDisplay statusCode={404} title="Module Not Found" message="Module not found" />

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
        <div className="mx-auto max-w-6xl">
          <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h1 className="text-2xl font-bold sm:text-3xl">{moduleData.name} Issues</h1>
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
          </div>

          <IssuesTable
            issues={moduleIssues}
            showAssignee={true}
            showDeadline={true}
            onIssueClick={handleIssueClick}
            emptyMessage="No issues found for the selected filter."
          />

          {/* Pagination Controls */}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            isLoaded={!loading}
          />
        </div>
      </div>
    </BreadcrumbStyleProvider>
  )
}

export default IssuesPage
