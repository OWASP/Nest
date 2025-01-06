import { useNavigate } from 'react-router-dom'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'
import { useSearchPage } from 'lib/hooks/useSearchPage'
import { user } from 'lib/types'
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
  } = useSearchPage<user>({
    indexName: 'users',
    pageTitle: 'OWASP Users',
  })

  const navigate = useNavigate()

  const handleButtonClick = (user: user) => {
    navigate(`/users/${user.idx_key}`)
  }

  const renderUserCard = (user: user) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: () => handleButtonClick(user),
    }

    return (
      <UserCard
        avatar={user.idx_avatar_url}
        name={user.idx_name}
        company={user.idx_company}
        button={SubmitButton}
      />
    )
  }

  return (
    <SearchPageLayout
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
        {users && users.map((user) => <div key={user.idx_key}>{renderUserCard(user)}</div>)}
      </div>
    </SearchPageLayout>
  )
}

export default UsersPage
