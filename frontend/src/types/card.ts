import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { JSX } from 'react'
import type { ButtonType } from 'types/button'
import type { Chapter } from 'types/chapter'
import type { TopContributors } from 'types/contributor'
import type { IconType } from 'types/icon'
import type { IssueType } from 'types/issue'
import type { Level } from 'types/level'
import type { MilestonesType } from 'types/milestone'
import type { RepositoryCardProps } from 'types/project'
import type { PullRequestType } from 'types/pullRequest'
import type { ReleaseType } from 'types/release'

export type CardProps = {
  button: ButtonType
  icons?: IconType
  isActive?: boolean
  level?: Level
  projectLink?: string
  projectName?: string
  social?: { title: string; icon: string; url: string }[]
  summary: string
  title: string
  tooltipLabel?: string
  topContributors?: TopContributors[]
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
  geolocationData?: Chapter[]
  heatmap?: JSX.Element
  isActive?: boolean
  languages?: string[]
  pullRequests?: PullRequestType[]
  recentIssues?: IssueType[]
  recentReleases?: ReleaseType[]
  recentMilestones?: MilestonesType[]
  repositories?: RepositoryCardProps[]
  socialLinks?: string[]
  stats?: stats[]
  summary?: string
  showAvatar?: boolean
  title?: string
  topContributors?: TopContributors[]
  topics?: string[]
  type: string
  userSummary?: JSX.Element
}

export interface UserCardProps {
  avatar: string
  button: ButtonType
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
  button: ButtonType
}
