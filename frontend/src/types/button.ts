import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { JSX } from 'react'

export type Button = {
  icon?: JSX.Element
  label: string
  onclick?: () => void
  url?: string
}

export type NavButtonProps = {
  className?: string
  defaultIcon: IconDefinition
  defaultIconColor?: string
  hoverIcon: IconDefinition
  hoverIconColor?: string
  href: string
  text: string
}
