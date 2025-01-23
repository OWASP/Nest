import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { JSX } from 'react'

export type ButtonType = {
  label: string
  icon?: JSX.Element
  onclick?: () => void
  url?: string
}

export interface NavButtonProps {
  href: string
  defaultIcon: IconDefinition
  hoverIcon: IconDefinition
  defaultIconColor?: string
  hoverIconColor?: string
  text: string
  className?: string
}
