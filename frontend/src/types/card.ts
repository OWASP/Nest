import { JSX } from 'react'
import { ButtonType } from './button'
import { GeoLocDataGraphQL } from './chapter'
import { TopContributorsTypeAlgolia, TopContributorsTypeGraphql } from './contributor'
import { IconType } from './icon'
import { Level } from './level'
import {
  ProjectIssuesType,
  ProjectReleaseType,
  ProjectStatsType,
  RepositoryCardProps,
} from './project'

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

export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  geolocationData?: GeoLocDataGraphQL
  is_active?: boolean
  languages?: string[]
  projectStats?: ProjectStatsType
  recentIssues?: ProjectIssuesType[]
  recentReleases?: ProjectReleaseType[]
  repositories?: RepositoryCardProps[]
  socialLinks?: string[]
  summary?: string
  title?: string
  topContributors?: TopContributorsTypeGraphql[]
  topics?: string[]
  type: string
}

export interface UserCardProps {
  avatar: string
  button: ButtonType
  company: string
  name: string
}
