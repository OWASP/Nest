'use client'

import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

export interface AlgoliaProgram {
  objectID: string
  name: string
  description: string
  experienceLevels: string[]
  status: string
  key: string
  admins: { name: string; login: string }[]
  startedAt: string
  endedAt: string
}

const ProgramsPage = () => {
  const {
    items: programs,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<AlgoliaProgram>({
    indexName: 'programs',
    pageTitle: 'OWASP Programs',
    hitsPerPage: 24,
  })

  const router = useRouter()

  const renderProgramCard = (program: AlgoliaProgram) => {
    const handleButtonClick = () => {
      router.push(`/mentorship/programs/${program.key}`)
    }

    const submitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <Card
        key={program.objectID}
        title={program.name}
        summary={program.description}
        button={submitButton}
        timeline={{
          start: program.startedAt,
          end: program.endedAt,
        }}
        url={`/mentorship/programs/${program.key}`}
      />
    )
  }

  return (
    <SearchPageLayout
      currentPage={currentPage}
      empty="No programs found"
      indexName="programs"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for programs..."
      searchQuery={searchQuery}
      totalPages={totalPages}
    >
      {programs && programs.filter((p) => p.status === 'published').map(renderProgramCard)}
    </SearchPageLayout>
  )
}

export default ProgramsPage
