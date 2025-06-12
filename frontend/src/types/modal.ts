import React from 'react'
import type { Button } from 'types/button'

export type ModalProps = {
  title: string
  summary: string
  hint?: string
  isOpen: boolean
  onClose: () => void
  button: Button
  children?: React.ReactNode
  description: string
}
