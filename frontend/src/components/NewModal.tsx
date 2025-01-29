import React from 'react';
import { Button, Text, Box, Stack, Separator} from '@chakra-ui/react';
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog'; // Import Dialog components

import { ModalProps } from 'types/modal';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBolt } from '@fortawesome/free-solid-svg-icons';
import Markdown from './MarkdownWrapper';
import ActionButton from './ActionButton';

const NewModal: React.FC<ModalProps> = ({
  title,
  summary,
  hint,
  isOpen,
  onClose,
  button,
  children,
}: ModalProps) => {
  return (
    <DialogRoot open={isOpen} onOpenChange={onClose} scrollBehavior="outside" size="xl" >
      <DialogContent my={9} p={7} className="animate-scaleIn relative z-50 w-full max-w-3xl transform rounded-lg bg-white p-6 shadow-xl backdrop-blur-sm transition-all duration-300 ease-in-out dark:border dark:border-gray-800 dark:bg-[#212529]"> 
        <DialogCloseTrigger className="absolute right-4 top-4 text-gray-400 hover:text-gray-600  dark:text-gray-500 dark:hover:text-gray-400 "
          aria-label="Close modal" />

        <DialogHeader fontSize="2xl" fontWeight="bold" color="gray.900" mb={1} className="text-2xl font-bold text-gray-900 dark:text-white">
          {title}
        </DialogHeader>


        <Text fontSize="xs" mb={1} className="text-gray-700 dark:text-gray-300/60">
          The issue summary and the recommended steps to address it have been generated by AI
        </Text>
   
        <Separator variant="solid" className="h-[.5px] bg-gray-300 my-[.3rem] inset-0 -m-7 border-gray-200 dark:bg-gray-700" />

       

        <DialogBody>
          <Text  mb={2} className="text-xl font-semibold">
            Issue Summary
          </Text>
          <Text className="text-base text-gray-600 dark:text-gray-300">
            {summary}
          </Text>
          {hint && (
            <Box className="rounded-md p-2 ">
              <Text fontSize="xl" className="space-x-2 text-xl font-semibold">
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
        <Separator  className="h-[.5px] bg-gray-300 my-[.3rem] inset-0 -m-7 border-gray-200 dark:bg-gray-700" />

        <DialogFooter className="mt-6 flex justify-end gap-4">
        <ActionButton url={button.url} onClick={button.onclick}>
            {button.icon}
            {button.label}
          </ActionButton>
          <Button variant="ghost" onClick={onClose} className="rounded-md bg-gray-600 px-4 py-1 text-sm font-medium text-white hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-600">
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </DialogRoot>
  );
};

export default NewModal;
