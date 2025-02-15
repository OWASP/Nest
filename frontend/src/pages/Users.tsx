import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { User } from 'types/user'
import { METADATA_CONFIG } from 'utils/metadata'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
import MetadataManager from 'components/MetadataManager'
import SearchPageLayout from 'components/SearchPageLayout'
import UserCard from 'components/UserCard'

const UsersPage = () => {
  const {
    items: users,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    handleSearch,
    handlePageChange,
  } = useSearchPage<User>({
    indexName: 'users',
    pageTitle: 'OWASP Users',
    hitsPerPage: 24,
  })

  const navigate = useNavigate()

  const handleButtonClick = (user: User) => {
    navigate(`/community/users/${user.key}`)
  }

  const renderUserCard = (user: User) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: () => handleButtonClick(user),
    }

    return (
      <UserCard
        avatar={user.avatar_url}
        name={user.name || `@${user.login}`}
        company={user.company}
        button={SubmitButton}
      />
    )
  }

  return (
    <MetadataManager {...METADATA_CONFIG.users}>
      <SearchPageLayout
        currentPage={currentPage}
        empty="No Users found"
        indexName="users"
        isLoaded={isLoaded}
        onPageChange={handlePageChange}
        onSearch={handleSearch}
        searchPlaceholder="Search for OWASP users..."
        searchQuery={searchQuery}
        totalPages={totalPages}
      >
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {users && users.map((user) => <div key={user.key}>{renderUserCard(user)}</div>)}
        </div>
      </SearchPageLayout>
    </MetadataManager>
  )
}

export default UsersPage
