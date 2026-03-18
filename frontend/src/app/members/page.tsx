'use client'

import { useSearchPage } from 'hooks/useSearchPage'
import { useRouter } from 'next/navigation'
import { useMemo, useState } from 'react'
import { FaRightToBracket } from 'react-icons/fa6'
import type { User } from 'types/user'
import { sortOptionsUser } from 'utils/sortingOptions'
import MembersFilter from 'components/MembersFilter'
import SearchPageLayout from 'components/SearchPageLayout'
import SortBy from 'components/SortBy'
import UserCard from 'components/UserCard'

const UsersPage = () => {
  const [selectedAffinity, setSelectedAffinity] = useState<string>('all')
  const [selectedMemberType, setSelectedMemberType] = useState<string>('all')

  const facetFilters = useMemo(() => {
    const filters: (string | string[])[] = []

    if (selectedAffinity === 'projects') {
      filters.push('idx_has_project_affinity:true')
    } else if (selectedAffinity === 'chapters') {
      filters.push('idx_has_chapter_affinity:true')
    } else if (selectedAffinity === 'committees') {
      filters.push('idx_has_committee_affinity:true')
    }

    if (selectedMemberType === 'staff') {
      filters.push('idx_is_owasp_staff:true')
    } else if (selectedMemberType === 'board') {
      filters.push('idx_owasp_board_member:true')
    } else if (selectedMemberType === 'gsoc') {
      filters.push('idx_owasp_gsoc_mentor:true')
    }

    return filters
  }, [selectedAffinity, selectedMemberType])

  const {
    items: users,
    isLoaded,
    currentPage,
    totalPages,
    searchQuery,
    sortBy,
    order,
    handleSearch,
    handlePageChange,
    handleSortChange,
    handleOrderChange,
  } = useSearchPage<User>({
    indexName: 'users',
    pageTitle: 'OWASP Users',
    defaultSortBy: 'default',
    defaultOrder: 'desc',
    hitsPerPage: 24,
    facetFilters,
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

    return (
      <UserCard
        avatar={user.avatarUrl}
        badgeCount={user.badgeCount || 0}
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
      filterChildren={
        <MembersFilter
          selectedAffinity={selectedAffinity}
          onAffinityChange={setSelectedAffinity}
          selectedMemberType={selectedMemberType}
          onMemberTypeChange={setSelectedMemberType}
        />
      }
      inlineSort
      sortChildren={
        <SortBy
          onOrderChange={handleOrderChange}
          onSortChange={handleSortChange}
          selectedOrder={order}
          selectedSortOption={sortBy}
          sortOptions={sortOptionsUser}
        />
      }
      totalPages={totalPages}
    >
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {users?.map((user) => (
          <div key={user.key}>{renderUserCard(user)}</div>
        ))}
      </div>
    </SearchPageLayout>
  )
}

export default UsersPage
