import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { JSX } from 'react'
import { ButtonType } from 'types/button'
import { Chapter } from 'types/chapter'
import { TopContributors } from 'types/contributor'
import { IconType } from 'types/icon'
import { Level } from 'types/level'
import {
  ProjectIssuesType,
  ProjectReleaseType,
  RepositoryCardProps,
  ProjectMilestonesType,
} from 'types/project'
import { ItemCardPullRequests } from 'types/user'

export interface CardProps {
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
  pullRequests?: ItemCardPullRequests[]
  recentIssues?: ProjectIssuesType[]
  recentReleases?: ProjectReleaseType[]
  recentMilestones?: ProjectMilestonesType[]
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
