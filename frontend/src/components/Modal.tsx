import { faBolt, faX } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useModal } from 'hooks/useModal'
import React, { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

import { ModalProps } from 'types/modal'
import Markdown from 'components/MarkdownWrapper'
import ActionButton from './ActionButton'

export const Modal: React.FC<ModalProps> = ({
  title,
  summary,
  hint,
  isOpen,
  onClose,
  button,
  children,
}) => {
  const modalRef = useRef<HTMLDivElement>(null)

  const { handleKeyDown } = useModal({ onClose, isOpen })

  useEffect(() => {
    if (isOpen) {
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth
      document.body.style.overflow = 'hidden'
      document.body.style.paddingRight = `${scrollbarWidth}px`
    } else {
      document.body.style.overflow = ''
      document.body.style.paddingRight = ''
    }

    return () => {
      document.body.style.overflow = ''
      document.body.style.paddingRight = ''
    }
  }, [isOpen])

  const handleOverlayClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
      onClose()
    }
  }

  const handleOverlayKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'Enter' || event.key === ' ') {
      handleOverlayClick(event as unknown as React.MouseEvent<HTMLDivElement>)
    }
  }

  if (!isOpen) return null

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto p-4 sm:p-10"
      role="presentation"
      onKeyDown={handleKeyDown}
    >
      {/* Overlay */}
      <div
        className="animate-fadeIn fixed inset-0 bg-black/30 transition-opacity"
        onClick={handleOverlayClick}
        onKeyDown={handleOverlayKeyDown}
        role="button"
        tabIndex={0}
        aria-label="Close modal overlay"
      />

      {/* Modal */}
      <div
        ref={modalRef}
        className="animate-scaleIn relative z-50 w-full max-w-3xl transform rounded-lg bg-white p-6 shadow-xl backdrop-blur-sm transition-all duration-300 ease-in-out dark:border dark:border-gray-800 dark:bg-[#212529]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:text-gray-500 dark:hover:text-gray-400 dark:focus:ring-gray-600"
          aria-label="Close modal"
        >
          <FontAwesomeIcon icon={faX} size="xs" />
        </button>

        {/* Content */}
        <div className="space-y-2">
          <h2 id="modal-title" className="text-2xl font-bold text-gray-900 dark:text-white">
            {title}
          </h2>
          <small className="text-gray-700 dark:text-gray-300/60">
            The issue summary and the recommended steps to address it have been generated by AI
          </small>
          <hr className="inset-0 -m-6 border-gray-200 dark:border-gray-700" />
          <h2 className="text-xl font-semibold">Issue Summary</h2>
          <Markdown content={summary} className="text-base text-gray-600 dark:text-gray-300" />
          {hint && (
            <div className="rounded-md p-2">
              <h2 className="space-x-2 text-xl font-semibold">
                <FontAwesomeIcon icon={faBolt} size="xs" />
                <span>How to tackle it</span>
              </h2>
              <Markdown
                content={hint}
                className="p-2 text-base text-gray-800 dark:border-white dark:text-gray-200"
              />
            </div>
          )}
          {children}
        </div>
        <hr className="inset-0 -mx-6 border-gray-200 dark:border-gray-700" />
        {/* Actions */}
        <div className="mt-6 flex justify-end gap-4">
          <ActionButton url={button.url} onClick={button.onclick}>
            {button.icon}
            {button.label}
          </ActionButton>
          <button
            onClick={onClose}
            className="rounded-md bg-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    </div>,
    document.body
  )
}
