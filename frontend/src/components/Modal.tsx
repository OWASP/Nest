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
}: ModalProps) => {
  return (
    <Modal isOpen={isOpen} size="4xl" scrollBehavior="inside" onClose={onClose}>
      <ModalContent
        className="animate-scaleIn relative z-50 my-9 w-full transform rounded-lg bg-white p-7 shadow-xl backdrop-blur-xs transition-all duration-300 ease-in-out dark:border-1 dark:border-gray-800 dark:bg-[#212529]"
        aria-labelledby="modal-title"
      >
        <ModalHeader className="mb-1 flex-col border-b-1 border-b-gray-200 text-2xl font-bold text-gray-900 dark:border-b-gray-700 dark:text-white">
          {title}
          <p className="text-xs text-gray-700 dark:text-gray-300/60">{description}</p>
        </ModalHeader>
        <ModalBody>
          <p className="mb-2 text-xl font-semibold">Summary</p>
          <Markdown className="text-base text-gray-600 dark:text-gray-300" content={summary} />
          {hint && (
            <div className="rounded-md p-2">
              <p className="flex flex-row items-center gap-2 text-xl font-semibold">
                <FaBolt size={14} /> How to tackle it
              </p>
              <Markdown
                className="p-2 text-base text-gray-800 dark:border-white dark:text-gray-200"
                content={hint}
              />
            </div>
          )}
          {children}
        </ModalBody>
        <div className="inset-0 -m-7 my-[.3rem] h-[.5px] border-gray-200 bg-gray-300 dark:bg-gray-700" />

        <ModalFooter className="mt-6 flex justify-end gap-4">
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
