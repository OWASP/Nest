import { ButtonType } from './button'
import { topContributorsType } from './contributor'
import { IconType } from './icon'
import { Level } from './level'

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
}
