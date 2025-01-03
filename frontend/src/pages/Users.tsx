import { useSearchPage } from 'lib/hooks/useSearchPage'
import { user } from 'lib/types'
import SearchPageLayout from 'components/SearchPageLayout'
import { useNavigate } from 'react-router-dom'
import FontAwesomeIconWrapper from 'lib/FontAwesomeIconWrapper'

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
    navigate(`/projects/${user.idx_key}`)
  }

  const renderUserCard = (user: user, index: number) => {
    const SubmitButton = {
      label: 'View Details',
      icon: <FontAwesomeIconWrapper icon="fa-solid fa-right-to-bracket" />,
      onclick: () => handleButtonClick(user),
    }

    return (
      <div
        key={index}
        className="bg-white shadow-md rounded-lg overflow-hidden p-2 my-2"
      >
        <div className="flex flex-col items-center justify-center">
          <div className="w-16 h-16 flex-shrink-0">
            <img
              src={user.idx_avatar_url}
              alt={`${user.idx_name} Avatar`}
              className="w-16 h-16 rounded-full object-cover"
            />
          </div>
          <div className="ml-4">
            <h3 className="text-xl font-semibold">{user.idx_name}</h3>
            <p className="text-gray-600">{user.idx_company}</p>
          </div>
        <div className="mt-4">
          <button
            onClick={SubmitButton.onclick}
            className="bg-blue-500 text-white rounded-md py-2 px-4 flex items-center"
          >
            {SubmitButton.icon}
            <span className="ml-2">{SubmitButton.label}</span>
          </button>
        </div>
        </div>
      </div>
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
