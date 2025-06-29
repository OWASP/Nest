'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import type { Organization } from 'types/organization'
import PageLayout from 'components/PageLayout'
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
  } = useSearchPage<Organization>({
    indexName: 'organizations',
    pageTitle: 'GitHub Organizations',
    hitsPerPage: 24,
  })

  const router = useRouter()

  const renderOrganizationCard = (organization: Organization) => {
    const handleButtonClick = () => {
      router.push(`/organizations/${organization.login}`)
    }

    const submitButton = {
      label: 'View Profile',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: handleButtonClick,
    }

    return (
      <UserCard
        avatar={organization.avatarUrl}
        button={submitButton}
        className="h-64 w-80 bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
        company={organization.company || ''}
        email={organization.email || ''}
        followersCount={organization.followersCount}
        key={organization.objectID}
        location={organization.location || `@${organization.login}`}
        name={organization.name}
        repositoriesCount={organization.publicRepositoriesCount}
      />
    )
  }

  return (
    <PageLayout>
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
    </PageLayout>
  )
}

export default OrganizationPage
