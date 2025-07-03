import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { JSX } from 'react'
import type { Button } from 'types/button'
import type { Chapter } from 'types/chapter'
import type { Contributor } from 'types/contributor'
import type { HealthMetricsProps } from 'types/healthMetrics'
import type { Icon } from 'types/icon'
import type { Issue } from 'types/issue'
import type { Level } from 'types/level'
import type { Milestone } from 'types/milestone'
import { Module } from 'types/program'
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
  social?: { title: string; icon: string; url: string }[]
  summary: string
  title: string
  timeline?: {
    start: string | Date
    end: string | Date
  }
  tooltipLabel?: string
  topContributors?: Contributor[]
  url: string
}

type stats = {
  icon: IconDefinition
  pluralizedName?: string
  unit?: string
  value: number
}
export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  domains?: string[]
  geolocationData?: Chapter[]
  heatmap?: JSX.Element
  healthMetricsData?: HealthMetricsProps[]
  isActive?: boolean
  languages?: string[]
  mentors?: Contributor[]
  admins?: Contributor[]
  pullRequests?: PullRequest[]
  recentIssues?: Issue[]
  recentReleases?: Release[]
  recentMilestones?: Milestone[]
  repositories?: RepositoryCardProps[]
  socialLinks?: string[]
  modules?: Module[]
  stats?: stats[]
  summary?: string
  showAvatar?: boolean
  title?: string
  topContributors?: Contributor[]
  topics?: string[]
  tags?: string[]
  type: string
  userSummary?: JSX.Element
}

export interface UserCardProps {
  avatar: string
  button: Button
  className?: string
  company?: string
  description?: string
  email?: string
  followersCount?: number
  location?: string
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
