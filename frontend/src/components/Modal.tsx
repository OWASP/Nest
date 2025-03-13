import { Button, Text, Box, Separator } from '@chakra-ui/react'
import { faBolt, faX } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react'
import { ModalProps } from 'types/modal'

import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogFooter,
} from 'components/ui/Dialog'
import ActionButton from './ActionButton'
import Markdown from './MarkdownWrapper'

const Modal: React.FC<ModalProps> = ({
  title,
  summary,
  hint,
  isOpen,
  onClose,
  button,
  children,
  description,
}: ModalProps) => {
  return (
    <DialogRoot
      open={isOpen}
      onEscapeKeyDown={onClose}
      unmountOnExit={true}
      onPointerDownOutside={onClose}
      scrollBehavior="outside"
      size="xl"
      role="dialog"
    >
      <DialogContent
        className="animate-scaleIn relative z-50 my-9 w-full max-w-3xl transform rounded-lg bg-white p-7 shadow-xl backdrop-blur-sm transition-all duration-300 ease-in-out dark:border dark:border-gray-800 dark:bg-[#212529]"
        aria-labelledby="modal-title"
      >
        <DialogCloseTrigger
          asChild={false}
          className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:text-gray-500 dark:hover:text-gray-400 dark:focus:ring-gray-600"
          aria-label="Close modal"
        >
          <FontAwesomeIcon icon={faX} size="xs" onClick={onClose} />
        </DialogCloseTrigger>

        <DialogHeader className="mb-1 text-2xl font-bold text-gray-900 dark:text-white">
          {title}
        </DialogHeader>
        <Text className="mb-1 text-xs text-gray-700 dark:text-gray-300/60">{description}</Text>
        <Separator
          variant="solid"
          className="inset-0 -m-7 my-[.3rem] h-[.5px] border-gray-200 bg-gray-300 dark:bg-gray-700"
        />

        <DialogBody>
          <Text className="mb-2 text-xl font-semibold">Summary</Text>
          <Markdown className="text-base text-gray-600 dark:text-gray-300" content={summary} />
          {hint && (
            <Box className="rounded-md p-2">
              <Text className="space-x-2 text-xl font-semibold">
                <FontAwesomeIcon icon={faBolt} size="xs" /> How to tackle it
              </Text>
              <Markdown
                className="p-2 text-base text-gray-800 dark:border-white dark:text-gray-200"
                content={hint}
              />
            </Box>
          )}
          {children}
        </DialogBody>
        <Separator className="inset-0 -m-7 my-[.3rem] h-[.5px] border-gray-200 bg-gray-300 dark:bg-gray-700" />

        <DialogFooter className="mt-6 flex justify-end gap-4">
          <ActionButton url={button.url} onClick={button.onclick}>
            {button.icon}
            {button.label}
          </ActionButton>
          <Button
            variant="ghost"
            onClick={onClose}
            aria-label="close-modal"
            className="rounded-md bg-gray-600 px-4 py-1 text-sm font-medium text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-600"
          >
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  )
}

export default Modal
