import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faEnvelope } from '@fortawesome/free-regular-svg-icons'
import {
  faBuildingUser,
  faCode,
  faCodeBranch,
  faLocationDot,
  faUserPlus,
  faUser,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { API_URL } from 'utils/credentials'
import logger from 'utils/logger'
import { UserDetailsProps } from 'lib/types'
import LoadingSpinner from 'components/LoadingSpinner'

const UserDetailsPage: React.FC = () => {
  const { login } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        setIsLoading(true)
        const response = await fetch(`${API_URL}/github/users/login/${login}`)
        const data = await response.json()
        setUser(data)
      } catch (error) {
        logger.error(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserData()
  }, [login])

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!user) {
    return <div className="flex h-screen items-center justify-center">User does not exist</div>
  }

  return (
    <div className="mt-24 min-h-screen w-full p-4">
      <div className="mx-auto md:max-w-3xl">
        <div className="overflow-hidden rounded-3xl bg-white shadow-xl dark:bg-gray-800">
          <div className="relative">
            <div className="h-32 bg-owasp-blue"></div>
            <div className="relative px-6">
              <div className="flex flex-col items-start justify-between sm:flex-row sm:space-x-6">
                <div className="flex flex-col items-center space-y-4 sm:flex-row sm:items-center sm:space-x-6 sm:space-y-0">
                  <div className="-mt-24 flex-shrink-0">
                    <img
                      className="h-40 w-40 rounded-full border-4 border-white object-cover shadow-lg dark:border-gray-800"
                      src={user.avatar_url}
                      alt={user.name}
                    />
                  </div>
                  <div className="mt-6 sm:mt-0 sm:pb-4">
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                      {user.name}
                    </h1>
                    <a
                      href={`https://www.github.com/${login}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-lg text-gray-700 decoration-dotted hover:underline hover:underline-offset-2 dark:text-gray-300"
                    >
                      @{user.login}
                    </a>
                  </div>
                </div>
                <a
                  href={user.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group mt-4 inline-flex items-center space-x-2 rounded-full bg-gray-200 px-4 py-2 align-top text-gray-800 transition-colors hover:bg-gray-300 dark:bg-gray-600/60 dark:text-white dark:hover:bg-gray-600 dark:hover:text-gray-200"
                >
                  <FontAwesomeIcon icon={faGithub} className="text-sm" />
                  <span>Visit GitHub Profile</span>
                </a>
              </div>
            </div>
          </div>
          <div className="px-6 py-6">
            {user.bio && (
              <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
                <FontAwesomeIcon icon={faCode} className="text-sm" />
                <p className="text-lg">{user.bio}</p>
              </div>
            )}

            <div className="mt-4 space-y-3">
              {user.company && (
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <FontAwesomeIcon icon={faBuildingUser} className="text-sm" />
                  <span>{user.company}</span>
                </div>
              )}
              {user.location && (
                <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                  <FontAwesomeIcon icon={faLocationDot} className="text-sm" />
                  <span>{user.location}</span>
                </div>
              )}
              {user.email && (
                <a
                  href={`mailto:${user.email}`}
                  className="flex items-center space-x-2 text-gray-600 decoration-dotted hover:underline hover:underline-offset-2 dark:text-gray-400"
                >
                  <FontAwesomeIcon icon={faEnvelope} className="text-sm" />
                  <span>{user.email}</span>
                </a>
              )}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 bg-gray-200 p-6 sm:grid-cols-3 dark:bg-gray-900">
            {[
              { icon: faUser, label: 'Followers', value: user.followers_count },
              { icon: faUserPlus, label: 'Following', value: user.following_count },
              {
                icon: faCodeBranch,
                label: 'Repositories',
                value: user.public_repositories_count,
              },
            ].map(({ icon: Icon, label, value }) => (
              <div
                key={label}
                className="flex flex-col items-center rounded-2xl bg-white p-6 shadow transition-transform hover:scale-105 dark:bg-gray-800"
              >
                <FontAwesomeIcon
                  icon={Icon}
                  className="mb-2 h-8 w-8 text-blue-600 dark:text-blue-400"
                />
                <span className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">
                  {value}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
              </div>
            ))}
          </div>
          <div className="border-t border-gray-200 px-6 py-4 text-center text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
            Joined{' '}
            {new Date(user.created_at).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric',
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserDetailsPage
