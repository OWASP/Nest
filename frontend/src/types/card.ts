import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { JSX } from 'react'
import { ButtonType } from 'types/button'
import { GeoLocDataGraphQL } from 'types/chapter'
import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from 'types/contributor'
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
  topContributors?: TopContributorsTypeGraphql[] | TopContributorsTypeAlgolia[]
  url: string
}

interface stats {
  icon: IconDefinition
  pluralizedName?: string
  unit?: string
  value: number
}
export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  geolocationData?: GeoLocDataGraphQL | null
  heatmap?: JSX.Element
  is_active?: boolean
  key?: string
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
  topContributors?: TopContributorsTypeGraphql[]
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
  followers_count?: number
  location?: string
  name?: string
  repositories_count?: number
}

export interface SnapshotCardProps {
  key: string
  startAt: string
  endAt: string
  title: string
  button: ButtonType
}
