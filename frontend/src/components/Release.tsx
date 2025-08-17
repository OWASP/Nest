import { faCalendar, faFolderOpen } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import React from 'react'
import type { Release as ReleaseTypes } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import { TruncatedText } from 'components/TruncatedText'

interface ReleaseProps {
  release: ReleaseTypes
  showAvatar?: boolean
}

const Release: React.FC<ReleaseProps> = ({ release, showAvatar = true }) => {
  const router = useRouter()
  const { name, tagName, publishedAt, author, organizationName, repositoryName } = release

  return (
    <div className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
      <div className="flex w-full flex-col justify-between">
        <div className="flex w-full items-center">
          {showAvatar && author && (
            <Tooltip
              closeDelay={100}
              content={author.name || author.login}
              id={`avatar-tooltip-${tagName}`}
              delay={100}
              placement="bottom"
              showArrow
            >
              <Link
                className="flex-shrink-0 text-blue-400 hover:underline"
                href={author.login ? `/members/${author.login}` : '#'}
              >
                <Image
                  alt={author.name || author.login}
                  className="mr-2 h-6 w-6 rounded-full"
                  height={24}
                  src={author.avatarUrl}
                  width={24}
                />
              </Link>
            </Tooltip>
          )}
          <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
            <Link
              className="text-blue-400 hover:underline"
              href={`https://github.com/${organizationName}/${repositoryName}/releases/tag/${tagName}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <TruncatedText text={name || tagName} />
            </Link>
          </h3>
        </div>
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-600 dark:text-gray-400">
          <div className="mr-4 flex items-center">
            <FontAwesomeIcon icon={faCalendar} className="mr-2 h-4 w-4" />
            <span>{formatDate(publishedAt)}</span>
          </div>
          <div className="flex flex-1 items-center overflow-hidden">
            <FontAwesomeIcon icon={faFolderOpen} className="mr-2 h-5 w-4" />
            <button
              className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-600 hover:underline dark:text-gray-400"
              disabled={!organizationName || !repositoryName}
              onClick={() => {
                const org = organizationName || ''
                const repo = repositoryName || ''
                if (!org || !repo) return
                router.push(`/organizations/${org}/repositories/${repo}`)
              }}
            >
              <TruncatedText text={repositoryName} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Release
