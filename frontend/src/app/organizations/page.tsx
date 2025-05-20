'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import { OrganizationTypeAlgolia } from 'types/organization'
import SearchPageLayout from 'components/SearchPageLayout'
import UserCard from 'components/UserCard'

const OrganizationPage = () => {
  const {
    items: organizations,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<OrganizationTypeAlgolia>({
    indexName: 'organizations',
    pageTitle: 'GitHub Organizations',
    hitsPerPage: 24,
  })

  const router = useRouter()

  const renderOrganizationCard = (organization: OrganizationTypeAlgolia) => {
    const handleButtonClick = () => {
      router.push(`/organizations/${organization.login}`)
    }

    const SubmitButton = {
      label: 'View Profile',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <UserCard
        avatar={organization.avatar_url}
        button={SubmitButton}
        company={organization.company || ''}
        email={organization.email || ''}
        followers_count={organization.followers_count}
        key={organization.objectID}
        location={organization.location || `@${organization.login}`}
        name={organization.name}
        repositories_count={organization.public_repositories_count}
        className="h-64 w-80 bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
      />
    )
  }

  return (
    <SearchPageLayout
      currentPage={currentPage}
      empty="No organizations found"
      indexName="organizations"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for organizations..."
      searchQuery={searchQuery}
      totalPages={totalPages}
    >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {organizations && organizations.map(renderOrganizationCard)}
      </div>
    </SearchPageLayout>
  )
}

export default OrganizationPage
