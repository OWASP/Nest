import type { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import type { JSX } from 'react'

export type Button = {
  label: string
  icon?: JSX.Element
  onclick?: () => void
  url?: string
}

export type NavButtonProps = {
  href: string
  defaultIcon: IconDefinition
  hoverIcon: IconDefinition
  defaultIconColor?: string
  hoverIconColor?: string
  text: string
  className?: string
}
