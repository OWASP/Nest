import React, { useCallback, useEffect } from 'react'

interface UseModalProps {
  onClose: () => void
  isOpen: boolean
}

export const useModal = ({ onClose, isOpen }: UseModalProps) => {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent | React.KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose()
      }
    },
    [isOpen, onClose]
  )

  const handleOverlayClick = (event: React.MouseEvent) => {
    if (event.target === event.currentTarget) {
      onClose()
    }
  }

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      return () => document.removeEventListener('keydown', handleKeyDown)
    }
  }, [isOpen, handleKeyDown])

  return {
    handleKeyDown,
    handleOverlayClick,
  }
}
