import { useSearchPage } from 'lib/hooks/useSearchPage'
import { user } from 'lib/types'
import SearchPageLayout from 'components/SearchPageLayout'

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

  const renderUserCard = (user: user, index: number) => {
    return (
       <div key={index}>{user.idx_name}</div>
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
      {users && users.map(renderUserCard)}
    </SearchPageLayout>
  )
}

export default UsersPage
