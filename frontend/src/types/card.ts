import type { JSX } from 'react'
import type { IconType } from 'react-icons'
import type { Badge } from 'types/badge'
import type { Button } from 'types/button'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import type { HealthMetricsProps } from 'types/healthMetrics'
import type { Icon } from 'types/icon'
import type { Issue } from 'types/issue'
import type { Leader } from 'types/leader'
import type { Level } from 'types/level'
import type { Module } from 'types/mentorship'
import type { Milestone } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequest } from 'types/pullRequest'
import type { Release } from 'types/release'
import type { ContributionStats } from 'utils/contributionDataUtils'
import type { CardType } from 'components/CardDetailsPage'

export type CardProps = {
  button: Button
  icons?: Icon
  isActive?: boolean
  level?: Level
  projectLink?: string
  projectName?: string
  social?: { title: string; icon: IconType; url: string }[]
  summary: string
  title: string
  timeline?: {
    start: string
    end: string
  }
  tooltipLabel?: string
  topContributors?: Contributor[]
  url: string
}

export type Stats = {
  icon: IconType
  pluralizedName?: string
  unit?: string
  value: number
}
export interface DetailsCardProps {
  accessLevel?: string
  contributionData?: Record<string, number>
  contributionStats?: ContributionStats
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  domains?: string[]
  endDate?: string
  entityLeaders?: Leader[]
  entityKey?: string
  geolocationData?: Chapter[]
  healthMetricsData?: HealthMetricsProps[]
  heatmap?: JSX.Element
  isActive?: boolean
  startDate?: string
  isArchived?: boolean
  labels?: string[]
  languages?: string[]
  status?: string
  setStatus?: (newStatus: string) => void
  canUpdateStatus?: boolean
  mentors?: Contributor[]
  mentees?: Contributor[]
  admins?: Contributor[]
  projectName?: string
  programKey?: string
  pullRequests?: PullRequest[]
  recentIssues?: Issue[]
  recentMilestones?: Milestone[]
  recentReleases?: Release[]
  repositories?: RepositoryCardProps[]
  modules?: Module[]
  showAvatar?: boolean
  socialLinks?: string[]
  stats?: Stats[]
  summary?: string
  title?: string
  topContributors?: Contributor[]
  topics?: string[]
  tags?: string[]
  type: CardType
  userSummary?: JSX.Element
}

export interface UserCardProps {
  avatar: string
  badgeCount?: number
  badges?: Badge[]
  button: Button
  className?: string
  company?: string
  description?: string
  email?: string
  followersCount?: number
  location?: string
  login?: string
  name?: string
  repositoriesCount?: number
}

export interface SnapshotCardProps {
  key: string
  startAt: string
  endAt: string
  title: string
  button: Button
}
