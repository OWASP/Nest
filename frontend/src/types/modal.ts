import React from 'react'
import type { ButtonType } from 'types/button'

export type ModalProps = {
  title: string
  summary: string
  hint?: string
  isOpen: boolean
  onClose: () => void
  button: ButtonType
  children?: React.ReactNode
  description: string
}
