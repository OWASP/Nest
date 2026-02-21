'use client'

import { useQuery } from '@apollo/client/react'
import { Select, SelectItem } from '@heroui/select'
import { BreadcrumbStyleProvider } from 'contexts/BreadcrumbContext'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { ErrorDisplay, handleAppError } from 'app/global-error'
import { GetModuleIssuesDocument } from 'types/__generated__/moduleQueries.generated'
import IssuesTable, { type IssueRow } from 'components/IssuesTable'
import LoadingSpinner from 'components/LoadingSpinner'
import Pagination from 'components/Pagination'

const ITEMS_PER_PAGE = 20
const LABEL_ALL = 'all'

const IssuesPage = () => {
  const { programKey, moduleKey } = useParams<{ programKey: string; moduleKey: string }>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [selectedLabel, setSelectedLabel] = useState<string>(searchParams.get('label') || LABEL_ALL)
  const [currentPage, setCurrentPage] = useState(1)

  const { data, loading, error } = useQuery(GetModuleIssuesDocument, {
    variables: {
      programKey,
      moduleKey,
      limit: ITEMS_PER_PAGE,
      offset: (currentPage - 1) * ITEMS_PER_PAGE,
      label: selectedLabel === LABEL_ALL ? null : selectedLabel,
    },
    skip: !programKey || !moduleKey,
    fetchPolicy: 'cache-and-network',
  })

  useEffect(() => {
    if (error) handleAppError(error)
  }, [error])

  const moduleData = data?.getModule

  const moduleIssues: IssueRow[] = useMemo(() => {
    return (moduleData?.issues || []).map((i) => ({
      objectID: i.id,
      number: i.number,
      title: i.title,
      state: i.state,
      isMerged: i.isMerged,
      labels: i.labels || [],
      assignees: i.assignees || [],
    }))
  }, [moduleData])

  const totalPages = Math.ceil((moduleData?.issuesCount || 0) / ITEMS_PER_PAGE)

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

  if (loading) return <LoadingSpinner />
  if (!moduleData)
    return <ErrorDisplay statusCode={404} title="Module Not Found" message="Module not found" />

  return (
    <BreadcrumbStyleProvider className="bg-white dark:bg-[#212529]">
      <div className="mt-16 min-h-screen bg-white p-8 text-gray-600 dark:bg-[#212529] dark:text-gray-300">
        <div className="mx-auto max-w-6xl">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold">{moduleData.name} Issues</h1>
            <div className="inline-flex h-12 items-center rounded-lg bg-gray-200 dark:bg-[#323232]">
              <Select
                labelPlacement="outside-left"
                size="md"
                aria-label="Filter by label"
                label="Label :"
                classNames={{
                  label:
                    'font-small text-sm text-gray-600 hover:cursor-pointer dark:text-gray-300 pl-[1.4rem] w-auto',
                  trigger: 'bg-gray-200 dark:bg-[#323232] pl-0 text-nowrap w-40',
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
          </div>

          <IssuesTable
            issues={moduleIssues}
            showAssignee={true}
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
