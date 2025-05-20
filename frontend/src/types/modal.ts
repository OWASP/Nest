import React from 'react'
import { ButtonType } from 'types/button'

export interface ModalProps {
  title: string
  summary: string
  hint?: string
  isOpen: boolean
  onClose: () => void
  button: ButtonType
  children?: React.ReactNode
  description: string
}
