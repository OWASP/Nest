'use client'

import { useSearchPage } from 'hooks/useSearchPage'
import { ProgramStatusEnum } from 'types/__generated__/graphql'
import { Program } from 'types/mentorship'
import ProgramCard from 'components/ProgramCard'
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
  } = useSearchPage<Program>({
    indexName: 'programs',
    pageTitle: 'OWASP Programs',
    hitsPerPage: 24,
  })

  const renderProgramCard = (program: Program) => {
    return (
      <ProgramCard
        accessLevel="user"
        isAdmin={false}
        key={program.key}
        href={`/mentorship/programs/${program.key}`}
        program={program}
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
      <div className="mt-16 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3">
        {programs &&
          programs
            .filter((p) => p.status?.toUpperCase() === ProgramStatusEnum.Published)
            .map(renderProgramCard)}
      </div>
    </SearchPageLayout>
  )
}

export default ProgramsPage
