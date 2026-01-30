import { capitalize } from 'lodash'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import React, { useState } from 'react'
import { FaChevronDown, FaChevronUp, FaTurnUp, FaCalendar, FaHourglassHalf, FaGripVertical } from 'react-icons/fa6'
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core'
import { SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, arrayMove } from '@dnd-kit/sortable'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { useMutation } from '@apollo/client'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { TextInfoItem } from 'components/InfoItem'
import SingleModuleCard from 'components/SingleModuleCard'
import { TruncatedText } from 'components/TruncatedText'
import { UPDATE_MODULE_POSITIONS } from 'server/queries/moduleQueries'

interface ModuleCardProps {
  modules: Module[]
  accessLevel?: string
  admins?: { login: string }[]
  programKey?: string
  enableReordering?: boolean
}

interface SortableModuleItemProps {
  module: Module
  programKey?: string
}

const SortableModuleItem = ({ module, programKey }: SortableModuleItemProps) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: module.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  const pathname = usePathname()

  const mentors = module.mentors || []
  const mentees = module.mentees || []

  const mentorsWithAvatars = mentors.filter((m) => m?.avatarUrl)
  const menteesWithAvatars = mentees.filter((m) => m?.avatarUrl)

  const moduleKey = module.key || module.id

  const getMenteeUrl = (login: string) => {
    if (pathname?.startsWith('/my/mentorship')) {
      return `/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${login}`
    }
    return `/members/${login}`
  }

  const getAvatarUrlWithSize = (avatarUrl: string): string => {
    try {
      const url = new URL(avatarUrl)
      url.searchParams.set('s', '60')
      return url.toString()
    } catch {
      const separator = avatarUrl.includes('?') ? '&' : '?'
      return `${avatarUrl}${separator}s=60`
    }
  }

  return (
    <div ref={setNodeRef} style={style} className="relative">
      <div className="absolute left-2 top-2 z-10 cursor-grab active:cursor-grabbing" {...attributes} {...listeners}>
        <FaGripVertical className="text-gray-400 hover:text-gray-600" />
      </div>
      <div className="flex h-auto min-h-[12rem] w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 pl-8 text-gray-600 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300">
        <Link
          href={`${pathname}/modules/${module.key}`}
          className="text-start font-semibold text-gray-600 hover:underline dark:text-gray-300"
        >
          <TruncatedText text={module?.name} />
        </Link>
        <TextInfoItem icon={FaTurnUp} label="Level" value={capitalize(module.experienceLevel)} />
        <TextInfoItem icon={FaCalendar} label="Start" value={formatDate(module.startedAt)} />
        <TextInfoItem
          icon={FaHourglassHalf}
          label="Duration"
          value={getSimpleDuration(module.startedAt, module.endedAt)}
        />

        {(mentorsWithAvatars.length > 0 || menteesWithAvatars.length > 0) && (
          <div className="mt-auto flex w-full gap-4">
            {mentorsWithAvatars.length > 0 && (
              <div className="flex flex-1 flex-col gap-2">
                <span className="text-xs font-bold tracking-wider text-gray-600 uppercase dark:text-gray-300">
                  Mentors
                </span>
                <div className="flex flex-wrap gap-1">
                  {mentorsWithAvatars.slice(0, 4).map((contributor) => (
                    <Link
                      key={contributor.login}
                      href={`/members/${contributor.login}`}
                      className="transition-opacity hover:opacity-80"
                    >
                      <Image
                        alt={contributor.name || contributor.login}
                        className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                        height={24}
                        src={getAvatarUrlWithSize(contributor.avatarUrl)}
                        title={contributor.name || contributor.login}
                        width={24}
                      />
                    </Link>
                  ))}
                  {mentorsWithAvatars.length > 4 && (
                    <span className="self-center text-xs font-medium text-gray-600 dark:text-gray-300">
                      +{mentorsWithAvatars.length - 4}
                    </span>
                  )}
                </div>
              </div>
            )}
            {menteesWithAvatars.length > 0 && (
              <div
                className={`flex flex-1 flex-col gap-2 ${mentorsWithAvatars.length > 0 ? 'border-l-1 border-gray-100 pl-4 dark:border-gray-700' : ''}`}
              >
                <span className="text-xs font-bold tracking-wider text-gray-600 uppercase dark:text-gray-300">
                  Mentees
                </span>
                <div className="flex flex-wrap gap-1">
                  {menteesWithAvatars.slice(0, 4).map((contributor) => (
                    <Link
                      key={contributor.login}
                      href={getMenteeUrl(contributor.login)}
                      className="transition-opacity hover:opacity-80"
                    >
                      <Image
                        alt={contributor.name || contributor.login}
                        className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                        height={24}
                        src={getAvatarUrlWithSize(contributor.avatarUrl)}
                        title={contributor.name || contributor.login}
                        width={24}
                      />
                    </Link>
                  ))}
                  {menteesWithAvatars.length > 4 && (
                    <span className="self-center text-xs font-medium text-gray-600 dark:text-gray-300">
                      +{menteesWithAvatars.length - 4}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

const ModuleCard = ({ modules, accessLevel, admins, programKey, enableReordering = false }: ModuleCardProps) => {
  const [showAllModule, setShowAllModule] = useState(false)
  const [modulesList, setModulesList] = useState(modules)
  
  const [updateModulePositions] = useMutation(UPDATE_MODULE_POSITIONS)
  
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  React.useEffect(() => {
    setModulesList(modules)
  }, [modules])

  const handleDragEnd = async (event: any) => {
    const { active, over } = event

    if (active.id !== over.id) {
      const oldIndex = modulesList.findIndex((module) => module.id === active.id)
      const newIndex = modulesList.findIndex((module) => module.id === over.id)
      
      const newModulesList = arrayMove(modulesList, oldIndex, newIndex)
      setModulesList(newModulesList)

      // Prepare module positions for mutation
      const modulePositions = newModulesList.map((module, index) => ({
        moduleId: module.id,
        position: index,
      }))

      try {
        await updateModulePositions({
          variables: {
            programKey,
            modulePositions,
          },
        })
      } catch (error) {
        console.error('Failed to update module positions:', error)
        // Revert to original order on error
        setModulesList(modules)
      }
    }
  }

  if (modules.length === 1) {
    return <SingleModuleCard module={modules[0]} accessLevel={accessLevel} admins={admins} />
  }

  const displayedModule = showAllModule ? modulesList : modulesList.slice(0, 4)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setShowAllModule(!showAllModule)
    }
  }

  if (enableReordering) {
    return (
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={modulesList.map((module) => module.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
            {displayedModule.map((module) => (
              <SortableModuleItem key={module.id} module={module} programKey={programKey} />
            ))}
          </div>
        </SortableContext>
        {modulesList.length > 4 && (
          <div className="mt-6 flex items-center justify-center text-center">
            <button
              type="button"
              onClick={() => setShowAllModule(!showAllModule)}
              onKeyDown={handleKeyDown}
              className="mt-4 flex items-center justify-center text-blue-400 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
            >
              {showAllModule ? (
                <>
                  Show less <FaChevronUp className="ml-1" />
                </>
              ) : (
                <>
                  Show more <FaChevronDown className="ml-1" />
                </>
              )}
            </button>
          </div>
        )}
      </DndContext>
    )
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
        {displayedModule.map((module) => {
          return <ModuleItem key={module.key || module.id} module={module} />
        })}
      </div>
      {modules.length > 4 && (
        <div className="mt-6 flex items-center justify-center text-center">
          <button
            type="button"
            onClick={() => setShowAllModule(!showAllModule)}
            onKeyDown={handleKeyDown}
            className="mt-4 flex items-center justify-center text-blue-400 hover:underline focus:rounded focus:outline-2 focus:outline-offset-2 focus:outline-blue-500"
          >
            {showAllModule ? (
              <>
                Show less <FaChevronUp className="ml-1" />
              </>
            ) : (
              <>
                Show more <FaChevronDown className="ml-1" />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

const ModuleItem = ({ module }: { module: Module }) => {
  const pathname = usePathname()

  const mentors = module.mentors || []
  const mentees = module.mentees || []

  const mentorsWithAvatars = mentors.filter((m) => m?.avatarUrl)
  const menteesWithAvatars = mentees.filter((m) => m?.avatarUrl)

  const programKey = pathname?.split('/programs/')[1]?.split('/')[0] || ''
  const moduleKey = module.key || module.id

  const getMenteeUrl = (login: string) => {
    if (pathname?.startsWith('/my/mentorship')) {
      return `/my/mentorship/programs/${programKey}/modules/${moduleKey}/mentees/${login}`
    }
    return `/members/${login}`
  }

  const getAvatarUrlWithSize = (avatarUrl: string): string => {
    try {
      const url = new URL(avatarUrl)
      url.searchParams.set('s', '60')
      return url.toString()
    } catch {
      const separator = avatarUrl.includes('?') ? '&' : '?'
      return `${avatarUrl}${separator}s=60`
    }
  }

  return (
    <div className="flex h-auto min-h-[12rem] w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 text-gray-600 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300">
      <Link
        href={`${pathname}/modules/${module.key}`}
        className="text-start font-semibold text-gray-600 hover:underline dark:text-gray-300"
      >
        <TruncatedText text={module?.name} />
      </Link>
      <TextInfoItem icon={FaTurnUp} label="Level" value={capitalize(module.experienceLevel)} />
      <TextInfoItem icon={FaCalendar} label="Start" value={formatDate(module.startedAt)} />
      <TextInfoItem
        icon={FaHourglassHalf}
        label="Duration"
        value={getSimpleDuration(module.startedAt, module.endedAt)}
      />

      {(mentorsWithAvatars.length > 0 || menteesWithAvatars.length > 0) && (
        <div className="mt-auto flex w-full gap-4">
          {mentorsWithAvatars.length > 0 && (
            <div className="flex flex-1 flex-col gap-2">
              <span className="text-xs font-bold tracking-wider text-gray-600 uppercase dark:text-gray-300">
                Mentors
              </span>
              <div className="flex flex-wrap gap-1">
                {mentorsWithAvatars.slice(0, 4).map((contributor) => (
                  <Link
                    key={contributor.login}
                    href={`/members/${contributor.login}`}
                    className="transition-opacity hover:opacity-80"
                  >
                    <Image
                      alt={contributor.name || contributor.login}
                      className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                      height={24}
                      src={getAvatarUrlWithSize(contributor.avatarUrl)}
                      title={contributor.name || contributor.login}
                      width={24}
                    />
                  </Link>
                ))}
                {mentorsWithAvatars.length > 4 && (
                  <span className="self-center text-xs font-medium text-gray-600 dark:text-gray-300">
                    +{mentorsWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
          {menteesWithAvatars.length > 0 && (
            <div
              className={`flex flex-1 flex-col gap-2 ${mentorsWithAvatars.length > 0 ? 'border-l-1 border-gray-100 pl-4 dark:border-gray-700' : ''}`}
            >
              <span className="text-xs font-bold tracking-wider text-gray-600 uppercase dark:text-gray-300">
                Mentees
              </span>
              <div className="flex flex-wrap gap-1">
                {menteesWithAvatars.slice(0, 4).map((contributor) => (
                  <Link
                    key={contributor.login}
                    href={getMenteeUrl(contributor.login)}
                    className="transition-opacity hover:opacity-80"
                  >
                    <Image
                      alt={contributor.name || contributor.login}
                      className="rounded-full border-1 border-gray-200 dark:border-gray-700"
                      height={24}
                      src={getAvatarUrlWithSize(contributor.avatarUrl)}
                      title={contributor.name || contributor.login}
                      width={24}
                    />
                  </Link>
                ))}
                {menteesWithAvatars.length > 4 && (
                  <span className="self-center text-xs font-medium text-gray-600 dark:text-gray-300">
                    +{menteesWithAvatars.length - 4}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ModuleCard

export const getSimpleDuration = (start: string | number, end: string | number): string => {
  if (!start || !end) return 'N/A'

  const startDate = typeof start === 'number' ? new Date(start * 1000) : new Date(start)
  const endDate = typeof end === 'number' ? new Date(end * 1000) : new Date(end)

  if (Number.isNaN(startDate.getTime()) || Number.isNaN(endDate.getTime())) {
    return 'Invalid duration'
  }

  const ms = endDate.getTime() - startDate.getTime()
  const days = Math.floor(ms / (1000 * 60 * 60 * 24))
  const weeks = Math.ceil(days / 7)

  return `${weeks} week${weeks === 1 ? '' : 's'}`
}
