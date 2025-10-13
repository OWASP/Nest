import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { JSX } from 'react'
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

export type CardProps = {
  button: Button
  icons?: Icon
  isActive?: boolean
  level?: Level
  projectLink?: string
  projectName?: string
  modules?: string[]
  social?: { title: string; icon: string; url: string }[]
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

type Stats = {
  icon: IconDefinition
  pluralizedName?: string
  unit?: string
  value: number
}
export interface DetailsCardProps {
  accessLevel?: string
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  domains?: string[]
  entityLeaders?: Leader[]
  entityKey?: string
  geolocationData?: Chapter[]
  healthMetricsData?: HealthMetricsProps[]
  heatmap?: JSX.Element
  isActive?: boolean
  languages?: string[]
  status?: string
  setStatus?: (newStatus: string) => void
  canUpdateStatus?: boolean
  mentors?: Contributor[]
  admins?: Contributor[]
  projectName?: string
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
  type: string
  userSummary?: JSX.Element
}

export interface UserCardProps {
  avatar: string
  badges?: Badge[]
  badgeCount?: number
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
