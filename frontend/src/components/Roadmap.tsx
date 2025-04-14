'use client'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import Link from 'next/link'
import { roadmap } from 'utils/aboutData'
import SecondaryCard from 'components/SecondaryCard'

const Roadmap = () => {
  return (
    <SecondaryCard title="Project Roadmap">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {roadmap.map((item, index) => (
          <div
            key={index}
            className="flex flex-col justify-between border p-4 text-gray-600 dark:border-gray-700 dark:text-gray-300"
          >
            <div className="flex items-start">
              <div className="mr-4 flex h-10 w-10 flex-none items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                <FontAwesomeIcon
                  icon={item.icon}
                  className="text-lg text-blue-600 dark:text-blue-400"
                />
              </div>
              <div className="flex flex-col">
                <div className="h-3/4">
                  {' '}
                  <h3 className="mb-1 text-lg font-semibold leading-snug">{item.title}</h3>
                  <p className="mb-4 line-clamp-3 text-sm">{item.detailedDescription}</p>
                </div>

                <div className="mt-auto h-1/4 pt-2">
                  <Link
                    href={item.issueLink}
                    target="_blank"
                    className="inline-flex items-center text-sm text-blue-500 dark:text-blue-400"
                    aria-label={`View GitHub Issue for ${item.title}`}
                  >
                    <FontAwesomeIcon icon={faGithub} className="mr-1" aria-hidden="true" />
                    View GitHub Issue
                  </Link>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </SecondaryCard>
  )
}

export default Roadmap
