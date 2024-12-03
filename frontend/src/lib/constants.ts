export type IconType = {
  [key: string]: string | number
}

export interface Level {
  color: string
  icon: string
  level?: string
}

export type topContributorsType = {
  avatar_url: string
  contributions_count: number
  login: string
  name: string
}

export type ButtonType = {
  label: string
  icon?: JSX.Element
  onclick?: () => void
  link?: string
}

export interface CardProps {
  title: string
  summary: string
  level?: Level
  icons?: IconType
  leaders?: string[]
  topContributors?: topContributorsType[]
  topics?: string[]
  button: ButtonType
  projectName?: string
  projectLink?: string
  languages?: string[]
  social?: { title: string; icon: string; url: string }[]
}

export const tooltipStyle = {
  backgroundColor: 'white',
  color: 'black',
}
