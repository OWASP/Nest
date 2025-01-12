import { JSX } from 'react'

export type ButtonType = {
  label: string
  icon?: JSX.Element
  onclick?: () => void
  url?: string
}
