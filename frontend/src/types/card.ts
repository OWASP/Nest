import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { JSX } from 'react'
import { ButtonType } from './button'
import { ChapterType } from './chapter'
import { topContributorsType } from './contributor'
import { IconType } from './icon'
import { Level } from './level'
import { ProjectIssuesType, ProjectReleaseType, RepositoryCardProps } from './project'

export interface UserCardProps {
  avatar: string
  name: string
  company: string
  button: ButtonType
}

export interface CardProps {
  title: string
  url: string
  summary: string
  level?: Level
  icons?: IconType
  topContributors?: topContributorsType[]
  button: ButtonType
  projectName?: string
  projectLink?: string
  social?: { title: string; icon: string; url: string }[]
  tooltipLabel?: string
  isActive?: boolean
}

interface stats {
  icon: IconDefinition
  value: string
}
export interface DetailsCardProps {
  description?: string
  details?: { label: string; value: string | JSX.Element }[]
  geolocationData?: ChapterType
  is_active?: boolean
  languages?: string[]
  socialLinks?: string[]
  stats?: stats[]
  summary?: string
  title?: string
  topContributors?: topContributorsType[]
  topics?: string[]
  type: string
  recentIssues?: ProjectIssuesType[]
  recentReleases?: ProjectReleaseType[]
  repositories?: RepositoryCardProps[]
}
