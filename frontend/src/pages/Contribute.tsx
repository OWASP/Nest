import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { useSearchPage } from 'hooks/useSearchPage'
import React, { useState } from 'react'

import { IssueType } from 'types/issue'
import { getFilteredIcons } from 'utils/utility'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'

import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'
import NewModal from 'components/NewModal'

const ContributePage = () => {
  const {
    items: issues,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<IssueType>({
    indexName: 'issues',
    pageTitle: 'OWASP Issues',
  })

  const [modalOpenIndex, setModalOpenIndex] = useState<number | null>(null)

  const renderContributeCard = (issue: IssueType, index: number) => {
    const params: string[] = ['created_at', 'comments_count']
    const filteredIcons = getFilteredIcons(issue, params)

    const SubmitButton = {
      label: 'Read More',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-wand-magic-sparkles" />,
      onclick: () => setModalOpenIndex(index),
    }

    const viewIssueButton = {
      label: 'View Issue',
      icon: <FontAwesomeIconWrapper icon={faGithub} />,
      url: issue.url,
    }

    return (
      <React.Fragment key={issue.objectID}>
        <Card
          key={issue.objectID}
          title={issue.title}
          url={issue.url}
          projectName={issue.project_name}
          projectLink={issue.project_url}
          summary={issue.summary}
          icons={filteredIcons}
          button={SubmitButton}
        />
        <NewModal
          key={`modal-${index}`}
          isOpen={modalOpenIndex === index}
          onClose={() => setModalOpenIndex(null)}
          title={issue.title}
          summary={issue.summary}
          hint={issue.hint}
          button={viewIssueButton}
        ></NewModal>
      </React.Fragment>
    )
  }

  return (
    <SearchPageLayout
      isLoaded={isLoaded}
      indexName="issues"
      totalPages={totalPages}
      currentPage={currentPage}
      searchQuery={searchQuery}
      onSearch={handleSearch}
      onPageChange={handlePageChange}
      searchPlaceholder="Search for OWASP issues..."
      empty="No issues found"
    >
      {issues && issues.map(renderContributeCard)}
    </SearchPageLayout>
  )
}

export default ContributePage
