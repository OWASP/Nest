import type React from 'react'
import type { JSX } from 'react'
import type { IconType } from 'react-icons'

export type Button = {
  icon?: JSX.Element
  label: string
  onclick?: () => void
  onkeydown?: (e: React.KeyboardEvent) => void
  url?: string
}

export type NavButtonProps = {
  className?: string
  defaultIcon: IconType
  defaultIconColor?: string
  hoverIcon: IconType
  hoverIconColor?: string
  href: string
  text: string
}
