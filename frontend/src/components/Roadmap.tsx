'use client'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faChevronUp, faChevronDown } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { useState } from 'react'
import { roadmap } from 'utils/aboutData'
import SecondaryCard from 'components/SecondaryCard'

const Roadmap = () => {
  const [expandedItem, setExpandedItem] = useState<number | null>(null)

  const toggleExpand = (index: number) => {
    if (expandedItem === index) {
      setExpandedItem(null)
    } else {
      setExpandedItem(index)
    }
  }

  return (
    <SecondaryCard title="Project Roadmap">
      <div className="space-y-8">
        {roadmap.map((item, index) => (
          <div
            key={index}
            className={`relative transform rounded-lg border p-5 shadow-sm transition-all duration-300 hover:translate-x-1 dark:border-gray-600 dark:bg-gray-700/30 ${
              expandedItem === index
                ? 'ring-1 ring-blue-400 dark:ring-blue-500'
                : 'hover:border-blue-200 dark:hover:border-blue-700'
            }`}
          >
            <button
              className="w-full text-left"
              onClick={() => toggleExpand(index)}
              aria-expanded={expandedItem === index}
              aria-controls={`roadmap-item-${index}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-grow">
                  <div className="mb-3 flex items-center">
                    <div className="mr-4 flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 shadow-sm dark:bg-blue-900">
                      <FontAwesomeIcon
                        icon={item.icon}
                        className="text-blue-600 dark:text-blue-400"
                      />
                    </div>
                    <h3 className="font-medium">{item.title}</h3>
                  </div>
                  <p className="ml-14 text-sm text-gray-600 dark:text-gray-300">
                    {item.description}
                  </p>
                </div>
                <div className="ml-2 flex-shrink-0 transform transition-transform duration-300 ease-in-out">
                  <FontAwesomeIcon
                    icon={expandedItem === index ? faChevronUp : faChevronDown}
                    className={`text-gray-500 transition-transform duration-300 dark:text-gray-400 ${expandedItem === index ? 'rotate-180' : 'rotate-0'}`}
                    aria-hidden="true"
                  />
                </div>
              </div>
            </button>

            {/* Expanding content inside the same box */}
            <div
              id={`roadmap-item-${index}`}
              className={`ml-14 overflow-hidden transition-all duration-300 ease-in-out ${
                expandedItem === index
                  ? 'mt-3 max-h-96 border-t pt-3 opacity-100 dark:border-gray-600'
                  : 'max-h-0 opacity-0'
              }`}
            >
              <p className="mb-4 text-sm">{item.detailedDescription}</p>
              <Link
                href={item.issueLink}
                target="_blank"
                className="inline-flex items-center text-sm text-blue-500 transition-all duration-200 hover:translate-x-1 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300"
                aria-label={`View GitHub Issue for ${item.title}`}
              >
                <FontAwesomeIcon icon={faGithub} className="mr-1" aria-hidden="true" />
                View GitHub Issue
              </Link>
            </div>
          </div>
        ))}
      </div>
    </SecondaryCard>
  )
}

export default Roadmap
