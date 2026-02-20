'use client'

import { gql } from '@apollo/client'
import { useMutation } from '@apollo/client/react'
import { Button } from '@heroui/button'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/modal'
import { addToast } from '@heroui/toast'
import { useRouter } from 'next/navigation'
import type React from 'react'
import { useState, useRef, useEffect } from 'react'
import { FaEllipsisV } from 'react-icons/fa'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { GetProgramAndModulesDocument } from 'types/__generated__/programsQueries.generated'

const DELETE_MODULE_MUTATION = gql`
  mutation DeleteModule($programKey: String!, $moduleKey: String!) {
    deleteModule(programKey: $programKey, moduleKey: $moduleKey)
  }
`

type DeleteModuleResponse = {
  deleteModule: boolean
}

interface EntityActionsProps {
  type: 'program' | 'module'
  programKey: string
  moduleKey?: string
  status?: string
  setStatus?: (newStatus: ProgramStatusEnum) => void | Promise<void>
  isAdmin?: boolean
}

const EntityActions: React.FC<EntityActionsProps> = ({
  type,
  programKey,
  moduleKey,
  status,
  setStatus,
  isAdmin = false,
}) => {
  const router = useRouter()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [deleteModalOpen, setDeleteModalOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [focusIndex, setFocusIndex] = useState(-1)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const triggerButtonRef = useRef<HTMLButtonElement>(null)
  const menuItemsRef = useRef<(HTMLButtonElement | null)[]>([])

  const [deleteModule] = useMutation<DeleteModuleResponse>(DELETE_MODULE_MUTATION)

  const handleAction = (actionKey: string) => {
    switch (actionKey) {
      case 'edit_program':
        router.push(`/my/mentorship/programs/${programKey}/edit`)
        break
      case 'create_module':
        router.push(`/my/mentorship/programs/${programKey}/modules/create`)
        break
      case 'edit_module':
        if (moduleKey) {
          router.push(`/my/mentorship/programs/${programKey}/modules/${moduleKey}/edit`)
        }
        break
      case 'view_issues':
        if (moduleKey) {
          router.push(`/my/mentorship/programs/${programKey}/modules/${moduleKey}/issues`)
        }
        break
      case 'delete_module':
        setDeleteModalOpen(true)
        break
      case 'publish':
        setStatus?.(ProgramStatusEnum.Published)
        break
      case 'draft':
        setStatus?.(ProgramStatusEnum.Draft)
        break
      case 'completed':
        setStatus?.(ProgramStatusEnum.Completed)
        break
    }
    setDropdownOpen(false)
  }

  const handleDeleteConfirm = async () => {
    if (!moduleKey) return

    setIsDeleting(true)

    try {
      const result = await deleteModule({
        variables: { programKey, moduleKey },

        update(cache) {
          const existing = cache.readQuery({
            query: GetProgramAndModulesDocument,
            variables: { programKey },
          })

          if (existing?.getProgramModules) {
            cache.writeQuery({
              query: GetProgramAndModulesDocument,
              variables: { programKey },
              data: {
                ...existing,
                getProgramModules: existing.getProgramModules.filter(
                  (module) => module.key !== moduleKey
                ),
              },
            })
          }
        },
      })

      if (!result?.data || typeof result.data !== 'object' || !result.data.deleteModule) {
        throw new Error('Delete mutation failed on server')
      }

      addToast({
        title: 'Success',
        description: 'Module has been deleted successfully.',
        color: 'success',
      })

      setDeleteModalOpen(false)
      router.push(`/my/mentorship/programs/${programKey}`)
    } catch (error) {
      let description = 'Failed to delete module. Please try again.'

      if (error instanceof Error) {
        if (error.message.includes('Permission') || error.message.includes('not have permission')) {
          description =
            'You do not have permission to delete this module. Only program admins can delete modules.'
        } else if (error.message.includes('Unauthorized')) {
          description = 'Unauthorized: You must be a program admin to delete modules.'
        }
      }

      addToast({
        title: 'Error',
        description,
        color: 'danger',
      })
    } finally {
      setIsDeleting(false)
    }
  }

  const options =
    type === 'program'
      ? [
          { key: 'edit_program', label: 'Edit' },
          { key: 'create_module', label: 'Add Module' },
          ...(status === ProgramStatusEnum.Draft ? [{ key: 'publish', label: 'Publish' }] : []),
          ...(status === ProgramStatusEnum.Published || status === ProgramStatusEnum.Completed
            ? [{ key: 'draft', label: 'Unpublish' }]
            : []),
          ...(status === ProgramStatusEnum.Published
            ? [{ key: 'completed', label: 'Mark as Completed' }]
            : []),
        ]
      : [
          { key: 'edit_module', label: 'Edit' },
          ...(isAdmin ? [{ key: 'view_issues', label: 'View Issues' }] : []),
          ...(isAdmin
            ? [{ key: 'delete_module', label: 'Delete', className: 'text-red-500' }]
            : []),
        ]

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
        setFocusIndex(-1)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  useEffect(() => {
    if (focusIndex >= 0 && menuItemsRef.current[focusIndex]) {
      menuItemsRef.current[focusIndex]?.focus()
    }
  }, [focusIndex])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const optionsCount = options.length

    switch (e.key) {
      case 'Escape':
        e.preventDefault()
        setDropdownOpen(false)
        setFocusIndex(-1)
        triggerButtonRef.current?.focus()
        break
      case 'ArrowDown':
        e.preventDefault()
        setFocusIndex((prev) => (prev < optionsCount - 1 ? prev + 1 : 0))
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusIndex((prev) => (prev > 0 ? prev - 1 : optionsCount - 1))
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        menuItemsRef.current[focusIndex]?.click()
        break
      default:
        break
    }
  }

  const handleToggle = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const newState = !dropdownOpen
    setDropdownOpen(newState)
    if (newState) {
      setFocusIndex(0)
    } else {
      setFocusIndex(-1)
    }
  }

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        <button
          ref={triggerButtonRef}
          type="button"
          onClick={handleToggle}
          className="cursor-pointer rounded px-4 py-2 hover:bg-gray-200 dark:hover:bg-gray-700"
          aria-label={`${type === 'program' ? 'Program' : 'Module'} actions menu`}
          aria-expanded={dropdownOpen}
          aria-haspopup="true"
        >
          <FaEllipsisV className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-200" />
        </button>
        {dropdownOpen && (
          <div
            className="absolute right-0 z-20 mt-2 w-40 rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
            onKeyDown={handleKeyDown}
            role="menu"
            tabIndex={0}
          >
            {options.map((option, index) => {
              const handleMenuItemClick = (e: React.MouseEvent) => {
                e.preventDefault()
                e.stopPropagation()
                handleAction(option.key)
                setFocusIndex(-1)
              }

              return (
                <button
                  key={option.key}
                  ref={(el) => {
                    menuItemsRef.current[index] = el
                  }}
                  type="button"
                  role="menuitem"
                  tabIndex={focusIndex === index ? 0 : -1}
                  onClick={handleMenuItemClick}
                  className={`block w-full cursor-pointer px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 ${
                    option.className || ''
                  }`}
                >
                  {option.label}
                </button>
              )
            })}
          </div>
        )}
      </div>

      {type === 'module' && (
        <Modal isOpen={deleteModalOpen} onClose={() => setDeleteModalOpen(false)}>
          <ModalContent>
            <ModalHeader className="flex flex-col gap-1">Delete Module</ModalHeader>
            <ModalBody>
              <p>Are you sure you want to delete this module? This action cannot be undone.</p>
            </ModalBody>
            <ModalFooter>
              <Button
                color="default"
                variant="light"
                onPress={() => setDeleteModalOpen(false)}
                disabled={isDeleting}
              >
                Cancel
              </Button>
              <Button
                color="danger"
                onPress={handleDeleteConfirm}
                isLoading={isDeleting}
                disabled={isDeleting}
                className="text-white"
              >
                Delete
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </>
  )
}

export default EntityActions
