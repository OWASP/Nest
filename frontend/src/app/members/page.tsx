'use client'
import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { FaRightToBracket } from 'react-icons/fa6'
import type { User } from 'types/user'
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

  const router = useRouter()
  const handleButtonClick = (user: User) => {
    router.push(`/members/${user.key}`)
  }

  const renderUserCard = (user: User) => {
    const submitButton = {
      label: 'View Details',
      icon: <FaRightToBracket className="h-4 w-4" />,
      onclick: () => handleButtonClick(user),
    }

    const badgeCount = user.badgeCount || 0
    return (
      <UserCard
        avatar={user.avatarUrl}
        badgeCount={badgeCount}
        badges={user.badges ?? []}
        button={submitButton}
        className="h-64 w-80 bg-white p-6 text-left shadow-lg transition-transform duration-500 hover:scale-105 hover:shadow-xl dark:bg-gray-800 dark:shadow-gray-900/30"
        company={user.company || ''}
        email={user.email || ''}
        followersCount={user.followersCount}
        location={user.location || ''}
        login={user.login}
        name={user.name || `@${user.login}`}
        repositoriesCount={user.publicRepositoriesCount}
      />
    )
  }

  return (
    <SearchPageLayout
      currentPage={currentPage}
      empty="No Users found"
      indexName="users"
      isLoaded={isLoaded}
      onPageChange={handlePageChange}
      onSearch={handleSearch}
      searchPlaceholder="Search for members..."
      searchQuery={searchQuery}
      totalPages={totalPages}
    >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {users && users.map((user) => <div key={user.key}>{renderUserCard(user)}</div>)}
      </div>
    </SearchPageLayout>
  )
}

export default UsersPage
