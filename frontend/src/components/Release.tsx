import { Tooltip } from '@heroui/tooltip'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import React from 'react'
import { FaCalendar, FaFolderOpen } from 'react-icons/fa6'
import type { Release as ReleaseType } from 'types/release'
import { formatDate } from 'utils/dateFormatter'
import { TruncatedText } from 'components/TruncatedText'

interface ReleaseProps {
  release: ReleaseType
  showAvatar?: boolean
  className?: string
  index?: number
}

const Release: React.FC<ReleaseProps> = ({
  release,
  showAvatar = true,
  className = '',
  index = 0,
}) => {
  const router = useRouter()
  const handleClickRepository = () => {
    const org = release.organizationName || ''
    const repo = release.repositoryName || ''
    if (!org || !repo) return
    router.push(`/organizations/${org}/repositories/${repo}`)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClickRepository()
    }
  }

  return (
    <div className={`mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700 ${className}`}>
      <div className="flex w-full flex-col justify-between">
        <div className="flex w-full items-center">
          {showAvatar && release?.author && (
            <Tooltip
              closeDelay={100}
              content={release.author.name || release.author.login}
              id={`avatar-tooltip-${index}`}
              delay={100}
              placement="bottom"
              showArrow
            >
              <Link
                className="shrink-0 text-blue-700 hover:underline dark:text-blue-300"
                href={release.author.login ? `/members/${release.author.login}` : '#'}
              >
                <Image
                  alt={
                    release.author && (release.author.name || release.author.login)
                      ? `${release.author.name || release.author.login}'s avatar`
                      : 'Release author avatar'
                  }
                  className="mr-2 h-6 w-6 rounded-full"
                  height={24}
                  src={release.author.avatarUrl}
                  width={24}
                />
              </Link>
            </Tooltip>
          )}
          <h3 className="min-w-0 flex-1 overflow-hidden font-semibold text-ellipsis whitespace-nowrap">
            <Link
              className="text-blue-700 hover:underline dark:text-blue-300"
              href={`https://github.com/${release.organizationName}/${release.repositoryName}/releases/tag/${release.tagName}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              <TruncatedText text={release.name || release.tagName} />
            </Link>
          </h3>
        </div>
        <div className="mt-2 flex flex-wrap items-center text-sm text-gray-800 dark:text-gray-200">
          <div className="mr-4 flex items-center">
            <FaCalendar className="mr-2 h-4 w-4" aria-hidden="true" />
            <span>{formatDate(release.publishedAt)}</span>
          </div>
          <div className="flex flex-1 items-center overflow-hidden">
            <FaFolderOpen className="mr-2 h-5 w-4 shrink-0" aria-hidden="true" />
            <button
              type="button"
              className="cursor-pointer overflow-hidden text-ellipsis whitespace-nowrap text-gray-800 hover:underline dark:text-gray-200"
              disabled={!release.organizationName || !release.repositoryName}
              onClick={handleClickRepository}
              onKeyDown={handleKeyDown}
              aria-label={`View repository ${release.repositoryName}`}
            >
              <TruncatedText text={release.repositoryName} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Release
