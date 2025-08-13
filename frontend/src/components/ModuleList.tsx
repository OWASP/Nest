import { faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Button } from '@heroui/button'
import React, { useState } from 'react'

interface ModuleListProps {
  modules: string[]
}

const ModuleList: React.FC<ModuleListProps> = ({ modules }) => {
  const [showAll, setShowAll] = useState(false)

  if (!modules || modules.length === 0) return null

  const displayedModules = showAll ? modules : modules.slice(0, 5)

  return (
    <div className="mt-3">
      <div className="flex flex-wrap items-center gap-2">
        {displayedModules.map((module, index) => {
          const displayText = module.length > 50 ? `${module.slice(0, 50)}...` : module
          return (
            <button
              key={`${module}-${index}`}
              className="rounded-lg border border-gray-400 px-3 py-1 text-sm transition-all duration-200 ease-in-out hover:scale-105 hover:bg-gray-200 dark:border-gray-300 dark:hover:bg-gray-700"
              title={module.length > 50 ? module : undefined}
              type="button"
            >
              {displayText}
            </button>
          )
        })}

        {modules.length > 5 && (
          <Button
            disableAnimation
            aria-label={showAll ? 'Show fewer modules' : 'Show more modules'}
            onPress={() => setShowAll((prev) => !prev)}
            className="mt-4 flex items-center bg-transparent text-blue-400 hover:underline"
          >
            {showAll ? (
              <>
                Show less <FontAwesomeIcon icon={faChevronUp} className="ml-1" />
              </>
            ) : (
              <>
                Show more <FontAwesomeIcon icon={faChevronDown} className="ml-1" />
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}

export default ModuleList
