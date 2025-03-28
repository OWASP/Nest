import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { JSX } from 'react'
import { ButtonType } from './button'
import { GeoLocDataGraphQL } from './chapter'
import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from './contributor'
import { IconType } from './icon'
import { Level } from './level'
import { ProjectIssuesType, ProjectReleaseType, RepositoryCardProps } from './project'
import { ItemCardPullRequests } from './user'

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
  value: string
}
export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  geolocationData?: GeoLocDataGraphQL
  heatmap?: JSX.Element
  is_active?: boolean
  languages?: string[]
  pullRequests?: ItemCardPullRequests[]
  recentIssues?: ProjectIssuesType[]
  recentReleases?: ProjectReleaseType[]
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
  company: string
  className?: string
  email: string
  location: string
  name: string
}
