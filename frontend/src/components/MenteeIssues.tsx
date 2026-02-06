import type React from 'react'
import { useState } from 'react'
import { FaBug, FaCheckCircle, FaClock } from 'react-icons/fa'
import { IconWrapper } from 'wrappers/IconWrapper'
import type { Issue } from 'types/issue'
import { formatDate } from 'utils/dateFormatter'
import { LabelList } from 'components/LabelList'
import SecondaryCard from 'components/SecondaryCard'

interface MenteeIssuesProps {
  openIssues: Issue[]
  closedIssues: Issue[]
  menteeHandle: string
}

const MenteeIssues: React.FC<MenteeIssuesProps> = ({ openIssues, closedIssues, menteeHandle }) => {
  const [activeTab, setActiveTab] = useState<'open' | 'closed'>('open')

  const getStateColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'open':
        return 'text-green-600 bg-green-100'
      case 'closed':
        return 'text-red-600 bg-red-100'
      case 'merged':
        return 'text-purple-600 bg-purple-100'
      default:
        return 'text-gray-800 bg-gray-100'
    }
  }

  const getStateIcon = (state: string) => {
    switch (state.toLowerCase()) {
      case 'open':
        return FaBug
      case 'closed':
        return FaCheckCircle
      default:
        return FaClock
    }
  }

  const renderIssueList = (issues: Issue[], title: string) => (
    <div className="space-y-3">
      {issues.length === 0 ? (
        <div className="py-8 text-center">
          <IconWrapper
            icon={activeTab === 'open' ? FaBug : FaCheckCircle}
            className="mx-auto mb-2 h-8 w-8 text-gray-400"
          />
          <p className="text-gray-500">No {title.toLowerCase()} issues</p>
        </div>
      ) : (
        issues.map((issue) => (
          <div
            key={issue.objectID}
            className="rounded-lg border border-gray-200 p-4 hover:bg-gray-50"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="mb-2 flex items-center space-x-2">
                  <IconWrapper
                    icon={getStateIcon(issue.state || 'open')}
                    className="h-4 w-4 text-gray-500"
                  />
                  <h4 className="line-clamp-2 font-medium text-gray-900">{issue.title}</h4>
                  <span
                    className={`rounded-full px-2 py-1 text-xs font-medium ${getStateColor(issue.state || 'open')}`}
                  >
                    {issue.state || 'open'}
                  </span>
                </div>

                {issue.labels && issue.labels.length > 0 && (
                  <div className="mb-2">
                    <LabelList
                      entityKey={`${issue.objectID}-labels`}
                      labels={issue.labels}
                      maxVisible={3}
                    />
                  </div>
                )}

                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>#{issue.number}</span>
                  <span>Created: {formatDate(issue.createdAt)}</span>
                  {issue.updatedAt && <span>Updated: {formatDate(issue.updatedAt)}</span>}
                </div>
              </div>

              <div className="ml-4 flex-shrink-0">
                <a
                  href={issue.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-blue-600 hover:text-blue-800"
                >
                  View Issue →
                </a>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  )

  return (
    <SecondaryCard icon={FaBug} title={`Issues for @${menteeHandle}`} className="gap-2">
      {/* Tab Navigation */}
      <div className="mb-4 flex border-b border-gray-200">
        <button
          type="button"
          onClick={() => setActiveTab('open')}
          className={`border-b-2 px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'open'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
        >
          <IconWrapper icon={FaBug} className="mr-2 h-4 w-4" />
          Open Issues ({openIssues.length})
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('closed')}
          className={`border-b-2 px-4 py-2 text-sm font-medium transition-colors ${activeTab === 'closed'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
        >
          <IconWrapper icon={FaCheckCircle} className="mr-2 h-4 w-4" />
          Closed Issues ({closedIssues.length})
        </button>
      </div>

      {/* Issue Content */}
      {activeTab === 'open'
        ? renderIssueList(openIssues, 'Open')
        : renderIssueList(closedIssues, 'Closed')}
    </SecondaryCard>
  )
}

export default MenteeIssues
