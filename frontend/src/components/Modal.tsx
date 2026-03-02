import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import React from 'react'
import { FaBolt } from 'react-icons/fa6'
import type { ModalProps } from 'types/modal'
import ActionButton from 'components/ActionButton'
import Markdown from 'components/MarkdownWrapper'

const DialogComp: React.FC<ModalProps> = ({
  title,
  summary,
  hint,
  onClose,
  isOpen,
  button,
  children,
  description,
}) => {
  return (
    <Modal isOpen={isOpen} size="lg" scrollBehavior="inside" onClose={onClose}>
      <ModalContent
        aria-labelledby="modal-title"
        className="animate-scaleIn relative z-50 flex max-h-[90vh] w-[95vw] max-w-4xl flex-col rounded-lg bg-white shadow-xl backdrop-blur-sm transition-all duration-300 ease-in-out sm:w-full dark:border dark:border-gray-800 dark:bg-[#212529]"
      >
        <ModalHeader className="flex flex-col gap-1 border-b border-gray-200 px-5 py-4 dark:border-gray-700">
          <h2
            id="modal-title"
            className="text-lg leading-snug font-bold [overflow-wrap:anywhere] break-words text-gray-900 sm:text-xl dark:text-white"
          >
            {title}
          </h2>

          {description && (
            <p className="text-xs text-gray-700 dark:text-gray-300/60">{description}</p>
          )}
        </ModalHeader>

        <ModalBody className="flex-1 overflow-y-auto px-5 py-4">
          <p className="mb-2 text-base font-semibold">Summary</p>

          <Markdown
            content={summary}
            className="text-base [overflow-wrap:anywhere] break-words text-gray-600 dark:text-gray-300"
          />

          {hint && (
            <div className="mt-4 rounded-md">
              <p className="mb-1 flex items-center gap-2 text-base font-semibold">
                <FaBolt size={14} />
                How to tackle it
              </p>

              <Markdown
                content={hint}
                className="text-base [overflow-wrap:anywhere] break-words text-gray-800 dark:text-gray-200"
              />
            </div>
          )}

          {children}
        </ModalBody>

        <ModalFooter className="sticky bottom-0 flex justify-end gap-4 border-t border-gray-200 bg-white px-5 py-4 dark:border-gray-700 dark:bg-[#212529]">
          <ActionButton url={button.url} onClick={button.onclick}>
            {button.icon}
            {button.label}
          </ActionButton>

          <Button
            variant="ghost"
            onPress={onClose}
            aria-label="close-modal"
            className="rounded-md bg-gray-600 px-4 py-1 text-sm font-medium text-white hover:bg-gray-700 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:outline-none dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-600"
          >
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}

export default DialogComp
