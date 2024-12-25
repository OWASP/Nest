import React from 'react'

export interface ModalProps {
  title: string
  summary: string
  hint?: string
  isOpen: boolean
  onClose: () => void
  children?: React.ReactNode
}
