import { useLazyQuery } from '@apollo/client/react'
import { useEffect, useState } from 'react'
import { FaCircleExclamation, FaCodePullRequest, FaTag } from 'react-icons/fa6'
import { handleAppError } from 'app/global-error'
import {
  GetSnapshotEntityPullRequestsDocument,
  GetSnapshotEntityIssuesDocument,
} from 'types/__generated__/snapshotQueries.generated'
import type { Issue } from 'types/issue'
import type { PullRequest } from 'types/pullRequest'
import type { Release as ReleaseType } from 'types/release'
import PaginationButtons from 'components/PaginationButtons'
import RecentIssues from 'components/RecentIssues'
import RecentPullRequests from 'components/RecentPullRequests'
import SecondaryCard from 'components/SecondaryCard'
import { ReleasesSection } from 'components/SnapshotReleaseSection'

const PR_LIMIT = 6
const ISSUE_LIMIT = 6

type SnapshotEntitySectionProps = {
  snapshotKey: string
  entityName: string
  entityType: string
  repositoryNames: string[]
  releases: ReleaseType[]
  initialPRs: PullRequest[]
  initialIssues: Issue[]
}

const SnapshotEntitySection = ({
  snapshotKey,
  entityName,
  entityType,
  repositoryNames,
  releases,
  initialPRs,
  initialIssues,
}: SnapshotEntitySectionProps) => {
  const [entityPRs, setEntityPRs] = useState<PullRequest[]>(initialPRs)
  const [prVisibleCount, setPrVisibleCount] = useState(PR_LIMIT)
  const [hasMorePRs, setHasMorePRs] = useState(initialPRs.length >= PR_LIMIT)
  const [isFetchingMorePRs, setIsFetchingMorePRs] = useState(false)
  const [entityIssues, setEntityIssues] = useState<Issue[]>(initialIssues)
  const [issueVisibleCount, setIssueVisibleCount] = useState(ISSUE_LIMIT)
  const [hasMoreIssues, setHasMoreIssues] = useState(initialIssues.length >= ISSUE_LIMIT)
  const [isFetchingMoreIssues, setIsFetchingMoreIssues] = useState(false)

  useEffect(() => {
    setEntityPRs(initialPRs)
    setPrVisibleCount(PR_LIMIT)
    setHasMorePRs(initialPRs.length >= PR_LIMIT)
  }, [initialPRs])

  useEffect(() => {
    setEntityIssues(initialIssues)
    setIssueVisibleCount(ISSUE_LIMIT)
    setHasMoreIssues(initialIssues.length >= ISSUE_LIMIT)
  }, [initialIssues])
  const [showAllReleases, setShowAllReleases] = useState(false)

  const [fetchEntityPRs] = useLazyQuery(GetSnapshotEntityPullRequestsDocument, {
    fetchPolicy: 'network-only',
  })

  const [fetchEntityIssues] = useLazyQuery(GetSnapshotEntityIssuesDocument, {
    fetchPolicy: 'network-only',
  })

  const handleShowMorePRs = () => {
    if (isFetchingMorePRs) return
    if (entityPRs.length > prVisibleCount) {
      setPrVisibleCount((prev) => Math.min(entityPRs.length, prev + PR_LIMIT))
      return
    }
    if (!hasMorePRs) return
    setIsFetchingMorePRs(true)
    fetchEntityPRs({
      variables: {
        key: snapshotKey,
        limit: PR_LIMIT,
        offset: entityPRs.length,
        repositoryNames,
      },
    })
      .then(({ data }) => {
        const newPRs = (data?.snapshot?.pullRequests || []) as PullRequest[]
        if (newPRs.length < PR_LIMIT) setHasMorePRs(false)
        if (newPRs.length > 0) {
          setEntityPRs((prev) => [...prev, ...newPRs])
          setPrVisibleCount((prev) => prev + newPRs.length)
        }
      })
      .catch((err) => handleAppError(err))
      .finally(() => setIsFetchingMorePRs(false))
  }

  const handleShowMoreIssues = () => {
    if (isFetchingMoreIssues) return
    if (entityIssues.length > issueVisibleCount) {
      setIssueVisibleCount((prev) => Math.min(entityIssues.length, prev + ISSUE_LIMIT))
      return
    }
    if (!hasMoreIssues) return
    setIsFetchingMoreIssues(true)
    fetchEntityIssues({
      variables: {
        key: snapshotKey,
        limit: ISSUE_LIMIT,
        offset: entityIssues.length,
        repositoryNames,
      },
    })
      .then(({ data }) => {
        const newIssues = (data?.snapshot?.issues || []) as Issue[]
        if (newIssues.length < ISSUE_LIMIT) setHasMoreIssues(false)
        if (newIssues.length > 0) {
          setEntityIssues((prev) => [...prev, ...newIssues])
          setIssueVisibleCount((prev) => prev + newIssues.length)
        }
      })
      .catch((err) => handleAppError(err))
      .finally(() => setIsFetchingMoreIssues(false))
  }

  const showPRSection = entityPRs.length > 0
  const showIssueSection = entityIssues.length > 0

  if (!showPRSection && !showIssueSection && releases.length === 0) {
    return null
  }

  const entityTitle = (
    <span className="flex items-baseline gap-3">
      <span className="text-2xl font-semibold">{entityName}</span>
      <span className="relative top-[-1px] rounded-full bg-blue-600/20 px-2.5 py-0.5 text-xs font-medium text-blue-400">
        {entityType}
      </span>
    </span>
  )

  return (
    <SecondaryCard title={entityTitle}>
      {showIssueSection && (
        <SecondaryCard icon={FaCircleExclamation} title="Issues">
          <RecentIssues
            data={entityIssues.slice(0, issueVisibleCount) as Issue[]}
            showBadge
            showSingleColumn={false}
            bare
          />
          <PaginationButtons
            onShowMore={handleShowMoreIssues}
            onShowLess={() => setIssueVisibleCount(ISSUE_LIMIT)}
            showMore={hasMoreIssues || entityIssues.length > issueVisibleCount}
            showLess={
              !isFetchingMoreIssues &&
              issueVisibleCount > ISSUE_LIMIT &&
              entityIssues.length > ISSUE_LIMIT
            }
            isLoading={isFetchingMoreIssues}
          />
        </SecondaryCard>
      )}

      {showPRSection && (
        <SecondaryCard icon={FaCodePullRequest} title="Pull Requests">
          <RecentPullRequests
            data={entityPRs.slice(0, prVisibleCount) as PullRequest[]}
            showBadge
            showSingleColumn={false}
            bare
          />
          <PaginationButtons
            onShowMore={handleShowMorePRs}
            onShowLess={() => setPrVisibleCount(PR_LIMIT)}
            showMore={hasMorePRs || entityPRs.length > prVisibleCount}
            showLess={
              !isFetchingMorePRs && prVisibleCount > PR_LIMIT && entityPRs.length > PR_LIMIT
            }
            isLoading={isFetchingMorePRs}
          />
        </SecondaryCard>
      )}

      {releases.length > 0 && (
        <SecondaryCard icon={FaTag} title="Releases">
          <ReleasesSection
            releases={releases}
            showAll={showAllReleases}
            onToggle={() => setShowAllReleases((prev) => !prev)}
          />
        </SecondaryCard>
      )}
    </SecondaryCard>
  )
}

export default SnapshotEntitySection
