import React from 'react'
import type { Button } from 'types/button'

export type ModalProps = {
  button: Button
  children?: React.ReactNode
  description: string
  hint?: string
  isOpen: boolean
  onClose: () => void
  summary: string
  title: string
}
