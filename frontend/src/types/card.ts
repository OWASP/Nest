import { JSX } from 'react'
import { ButtonType } from './button'
import { GeoLocData } from './chapter'
import { TopContributorsType } from './contributor'
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
  topContributors?: TopContributorsType[]
  url: string
}

export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  geolocationData?: GeoLocData
  is_active?: boolean
  languages?: string[]
  projectStats?: ProjectStatsType
  socialLinks?: string[]
  summary?: string
  title?: string
  topContributors?: TopContributorsType[]
  topics?: string[]
  type: string
  recentIssues?: ProjectIssuesType[]
  recentReleases?: ProjectReleaseType[]
  repositories?: RepositoryCardProps[]
}

export interface UserCardProps {
  avatar: string
  button: ButtonType
  company: string
  name: string
}
