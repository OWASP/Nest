'use client'

import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { ProgramList } from 'types/mentorship'
import Card from 'components/Card'
import SearchPageLayout from 'components/SearchPageLayout'

const ProgramsPage = () => {
  const {
    items: programs,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<ProgramList>({
    indexName: 'programs',
    pageTitle: 'OWASP Programs',
    hitsPerPage: 24,
  })

  const router = useRouter()

  const renderProgramCard = (program: ProgramList) => {
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
        key={program.key}
        title={program.name}
        summary={program.description}
        button={submitButton}
        timeline={{
          start: program.startedAt,
          end: program.endedAt,
        }}
        modules={program.modules}
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
