import {
  DndContext,
  DragOverlay,
  closestCorners,
  DragStartEvent,
  DragEndEvent,
  UniqueIdentifier,
} from '@dnd-kit/core'
import { SortableContext, arrayMove, rectSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { Button } from '@heroui/button'
import upperFirst from 'lodash/upperFirst'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type React from 'react'
import { useState } from 'react'
import {
  FaChevronDown,
  FaChevronUp,
  FaTurnUp,
  FaCalendar,
  FaHourglassHalf,
  FaGripVertical,
} from 'react-icons/fa6'
import type { Module } from 'types/mentorship'
import { formatDate } from 'utils/dateFormatter'
import { TextInfoItem } from 'components/InfoItem'
import { LabelList } from 'components/LabelList'
import SingleModuleCard from 'components/SingleModuleCard'
import { TruncatedText } from 'components/TruncatedText'

interface ModuleCardProps {
  modules: Module[]
  accessLevel?: string
  admins?: { login: string }[]
  setModuleOrder?: (order: Module[]) => void
}

const ModuleCard = ({ modules, accessLevel, admins, setModuleOrder }: ModuleCardProps) => {
  const [showAllModule, setShowAllModule] = useState(false)
  const [isReordering, setIsReordering] = useState(false)
  const [draftModules, setDraftModules] = useState<Module[] | null>(null)
  const [activeId, setActiveId] = useState<UniqueIdentifier | null>(null)

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id)
  }

  if (modules.length === 1) {
    return <SingleModuleCard module={modules[0]} accessLevel={accessLevel} admins={admins} />
  }
  const currentModules = isReordering ? draftModules! : modules
  const displayedModule = showAllModule ? currentModules : currentModules.slice(0, 4)
  const isAdmin = accessLevel === 'admin'

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setShowAllModule(!showAllModule)
    }
  }
  const startReorder = () => {
    setDraftModules(modules)
    setIsReordering(true)
  }
  const cancelReorder = () => {
    setDraftModules(null)
    setIsReordering(false)
    setActiveId(null)
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    setDraftModules((items) => {
      if (!items) return items
      const oldIndex = items.findIndex((m) => m.id === active.id)
      const newIndex = items.findIndex((m) => m.id === over.id)
      return arrayMove(items, oldIndex, newIndex)
    })
    setActiveId(null)
  }
  const saveReorder = () => {
    if (setModuleOrder && draftModules) {
      setModuleOrder(draftModules)
    }
    setIsReordering(false)
    setDraftModules(null)
  }

  return (
    <div>
      {isAdmin && (
        <div className="mb-4 flex gap-2">
          {!isReordering ? (
            <button onClick={startReorder} className="text-blue-400 hover:underline">
              Customize order
            </button>
          ) : (
            <>
              <Button type="button" onPress={saveReorder} color="primary" className="font-medium">
                Save order
              </Button>
              <Button
                type="button"
                variant="bordered"
                onPress={cancelReorder}
                className="font-medium"
              >
                Cancel
              </Button>
            </>
          )}
        </div>
      )}
      <DndContext
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={cancelReorder}
      >
        <SortableContext items={displayedModule.map((m) => m.id)} strategy={rectSortingStrategy}>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {displayedModule.map((module) => {
              return (
                <ModuleItem
                  key={module.key}
                  module={module}
                  isAdmin={isAdmin}
                  isReordering={isReordering}
                  activeId={activeId}
                />
              )
            })}
          </div>
        </SortableContext>
        <DragOverlay>
          {activeId && currentModules.find((m) => m.id === activeId) ? (
            <ModuleItem
              module={currentModules.find((m) => m.id === activeId)!}
              isAdmin={isAdmin}
              isReordering={isReordering}
              isOverlay
            />
          ) : null}
        </DragOverlay>
      </DndContext>
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

const ModuleItem = ({
  module,
  isAdmin,
  isReordering,
  activeId,
  isOverlay,
}: {
  module: Module
  isAdmin: boolean
  isReordering: boolean
  activeId?: UniqueIdentifier | null
  isOverlay?: boolean
}) => {
  const pathname = usePathname()
  const { setNodeRef, transform, transition, attributes, listeners, isDragging } = useSortable({
    id: module.id,
    disabled: !isReordering,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging || isOverlay ? 0.5 : 1,
  }

  const shouldHideOriginal = isDragging && activeId === module.id && !isOverlay

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`relative flex h-46 w-full flex-col gap-3 rounded-lg border-1 border-gray-200 p-4 shadow-xs ease-in-out hover:shadow-md dark:border-gray-700 dark:bg-gray-800 ${shouldHideOriginal ? 'invisible' : ''}`}
    >
      {isAdmin && isReordering && (
        <button
          {...attributes}
          {...listeners}
          className="absolute top-2 right-2 cursor-grab text-gray-400"
        >
          <FaGripVertical />
        </button>
      )}
      <Link
        href={`${pathname}/modules/${module.key}`}
        className="text-start font-semibold text-blue-400 hover:underline"
      >
        <TruncatedText text={module?.name} />
      </Link>
      <TextInfoItem icon={FaTurnUp} label="Level" value={upperFirst(module.experienceLevel)} />
      <TextInfoItem icon={FaCalendar} label="Start" value={formatDate(module.startedAt)} />
      <TextInfoItem
        icon={FaHourglassHalf}
        label="Duration"
        value={getSimpleDuration(module.startedAt, module.endedAt)}
      />
      {isAdmin && module.labels && module.labels.length > 0 && (
        <div className="mt-2">
          <LabelList labels={module.labels} maxVisible={3} />
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
  return `${weeks} week${weeks !== 1 ? 's' : ''}`
}
