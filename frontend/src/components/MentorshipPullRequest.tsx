import Image from 'next/image'
import Link from 'next/link'
import React from 'react'
import type { PullRequest } from 'types/pullRequest'
import { TruncatedText } from 'components/TruncatedText'

interface MentorshipPullRequestProps {
  pr: PullRequest
}

export const getPRStatus = (pr: PullRequest) => {
  let backgroundColor: string
  let label: string
  if (pr.state === 'closed' && pr.mergedAt) {
    backgroundColor = '#8657E5'
    label = 'Merged'
  } else if (pr.state === 'closed') {
    backgroundColor = '#DA3633'
    label = 'Closed'
  } else {
    backgroundColor = '#238636'
    label = 'Open'
  }
  return { backgroundColor, label }
}

const MentorshipPullRequest: React.FC<MentorshipPullRequestProps> = ({ pr }) => {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-gray-200 p-4 dark:bg-gray-700">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        {pr.author?.avatarUrl ? (
          <Image
            src={pr.author.avatarUrl}
            alt={pr.author?.login || 'Unknown'}
            width={32}
            height={32}
            className="flex-shrink-0 rounded-full"
          />
        ) : (
          <div className="h-8 w-8 flex-shrink-0 rounded-full bg-gray-400" aria-hidden="true" />
        )}
        <div className="min-w-0 flex-1">
          <Link
            href={pr.url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-blue-600 hover:text-blue-800 dark:text-blue-300 dark:hover:text-blue-300"
          >
            <TruncatedText text={pr.title} />
          </Link>
          <div className="text-sm text-gray-500 dark:text-gray-200">
            by {pr.author?.login || 'Unknown'} • {new Date(pr.createdAt).toLocaleDateString()}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-2">
        {(() => {
          const { backgroundColor, label } = getPRStatus(pr)
          return (
            <span
              className="inline-flex items-center rounded-lg px-2 py-0.5 text-xs font-medium text-white"
              style={{ backgroundColor }}
            >
              {label}
            </span>
          )
        })()}
      </div>
    </div>
  )
}

export default MentorshipPullRequest
