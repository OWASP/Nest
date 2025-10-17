import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { ReactElement } from 'react'

export interface HeaderSectionProps {
  title: string
  type: string
  accessLevel: string
  status: string
  setStatus: (status: string) => void
  canUpdateStatus: boolean
  admins?: Array<{ login: string }>
  description: string
  userLogin?: string
  router: any
  isActive: boolean
  healthMetricsData: Array<{ score: number }>
}

export interface SummarySectionProps {
  summary?: string
  userSummary?: ReactElement
}

export interface DetailsSectionProps {
  details: Array<{ label: string; value: string | number }>
  socialLinks?: string[]
  type: string
  geolocationData: { lat: number; lng: number } | null
}

export interface MetricsSectionProps {
  stats: Array<{
    icon: IconDefinition
    pluralizedName: string
    unit: string
    value: number
  }>
  type: string
}

export interface ListsSectionProps {
  languages?: string[]
  topics?: string[]
  tags?: string[]
  domains?: string[]
  type: string
}

export interface Contributor {
  login: string
  contributions?: number
  avatarUrl: string
  name: string
}

export interface ContributorsSectionProps {
  topContributors: Contributor[] | null
  admins?: Contributor[]
  mentors?: Contributor[]
  type: string
}

export interface Issue {
  title: string
  number: number
  url: string
  createdAt: number
  updatedAt?: number
}

export interface PullRequest {
  title: string
  number: number
  url: string
  createdAt: number
}

export interface Milestone {
  title: string
  description: string
  dueDate?: number
}

export interface Release {
  title: string
  description: string
  publishedAt: number
}

export interface ActivitySectionProps {
  type: string
  recentIssues: Issue[]
  pullRequests: PullRequest[]
  recentMilestones: Milestone[]
  recentReleases: Release[]
  showAvatar: boolean
}
