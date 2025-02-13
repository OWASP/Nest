import { useSearchPage } from 'hooks/useSearchPage'
import { useNavigate } from 'react-router-dom'
import { User } from 'types/user'
import FontAwesomeIconWrapper from 'wrappers/FontAwesomeIconWrapper'
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
    <SearchPageLayout
      indexName="users"
      isLoaded={isLoaded}
      totalPages={totalPages}
      currentPage={currentPage}
      searchQuery={searchQuery}
      onSearch={handleSearch}
      onPageChange={handlePageChange}
      empty="No Users found"
      searchPlaceholder="Search for OWASP users..."
    >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {users && users.map((user) => <div key={user.key}>{renderUserCard(user)}</div>)}
      </div>
    </SearchPageLayout>
  )
}

export default UsersPage
