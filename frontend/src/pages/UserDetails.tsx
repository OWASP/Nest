import { Link } from '@chakra-ui/react'
import { faGithub } from '@fortawesome/free-brands-svg-icons'
import { faEnvelope } from '@fortawesome/free-regular-svg-icons'
import {
  faBuildingUser,
  faCodeBranch,
  faLocationDot,
  faUserPlus,
  faUser,
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { fetchAlgoliaData } from 'api/fetchAlgoliaData'
import React, { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { UserDetailsProps } from 'types/user'
import { formatDate } from 'utils/dateFormatter'
import { fetchHeatmapData, drawContributions, HeatmapData } from 'utils/helpers/githubHeatmap'
import logger from 'utils/logger'
import { ErrorDisplay } from 'wrappers/ErrorWrapper'
import LoadingSpinner from 'components/LoadingSpinner'

const UserDetailsPage: React.FC = () => {
  const { userKey } = useParams()
  const [user, setUser] = useState<UserDetailsProps | null>()
  const [isLoading, setIsLoading] = useState(true)
  const [data, setData] = useState<HeatmapData | null>(null)
  const [username, setUsername] = useState('')
  const [imageLink, setImageLink] = useState('')
  const [privateContributor, setPrivateContributor] = useState(false)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const theme = 'blue'

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const { hits } = await fetchAlgoliaData('users', userKey, 1, userKey)
        if (hits.length === 0) {
          setUser(null)
        } else {
          setUser(hits[0] as unknown as UserDetailsProps)
        }
      } catch (error) {
        logger.error(error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserData()
  }, [userKey])

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchHeatmapData(userKey)
      if (result && result.contributions) {
        setUsername(userKey)
        setData(result)
      } else {
        setPrivateContributor(true)
      }
    }
    fetchData()
  }, [userKey, user])

  useEffect(() => {
    if (canvasRef.current && data && data.years && data.years.length > 0) {
      drawContributions(canvasRef.current, { data, username, theme })
      const imageURL = canvasRef.current.toDataURL()
      setImageLink(imageURL)
    }
  }, [username, data])

  if (isLoading)
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingSpinner imageUrl="/img/owasp_icon_white_sm.png" />
      </div>
    )

  if (!isLoading && user == null) {
    return (
      <ErrorDisplay
        statusCode={404}
        title="User not found"
        message="Sorry, the user you're looking for doesn't exist"
      />
    )
  }

  return (
    <div className="mt-24 min-h-screen w-full p-4">
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
      <div className="mx-auto md:max-w-3xl">
        <div className="overflow-hidden rounded-3xl bg-white shadow-xl dark:bg-gray-800">
          <div className="relative">
            {privateContributor ? (
              <div className="h-32 bg-owasp-blue"></div>
            ) : imageLink ? (
              <div className="bg-#10151c h-32">
                <img src={imageLink} className="h-full w-full object-cover object-[54%_60%]" />
              </div>
            ) : (
              <div className="bg-#10151c relative h-32 items-center justify-center">
                <img
                  src="/img/heatmapBackground.png"
                  className="heatmap-background-loader h-full w-full border-none object-cover object-[54%_60%]"
                />
                <div className="heatmap-loader"></div>
              </div>
            )}
            <div className="relative px-6">
              <div className="flex flex-col items-start justify-between sm:flex-row sm:space-x-6">
                <div className="flex flex-col items-center space-y-4 sm:flex-row sm:items-center sm:space-x-6 sm:space-y-0">
                  <div className="-mt-24 flex-shrink-0">
                    <img
                      className="h-40 w-40 rounded-full border-4 border-white bg-white object-cover shadow-lg transition-colors dark:border-gray-800 dark:bg-gray-600/60"
                      src={user.avatar_url}
                      alt={user.name}
                    />
                  </div>
                  <div className="mt-6 sm:mt-0 sm:pb-4">
                    <h1 className="text-nowrap text-3xl font-bold text-gray-900 dark:text-white">
                      {user.name}
                    </h1>
                    <Link
                      href={`https://www.github.com/${user.login}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-lg text-gray-700 decoration-dotted hover:underline hover:underline-offset-2 dark:text-gray-300"
                    >
                      @{user.login}
                    </Link>
                  </div>
                </div>
                <Link
                  href={user.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group mt-4 inline-flex flex-nowrap items-center space-x-2 text-nowrap rounded-full bg-gray-200 px-4 py-2 align-top text-gray-800 transition-colors hover:bg-gray-300 dark:bg-gray-600/60 dark:text-white dark:hover:bg-gray-600 dark:hover:text-gray-200"
                >
                  <FontAwesomeIcon icon={faGithub} className="text-sm" />
                  <span>Visit GitHub Profile</span>
                </Link>
              </div>
            </div>
          </div>
          <div className="px-6 py-6">
            {user.bio && <p className="text-lg text-gray-700 dark:text-gray-300">{user.bio}</p>}

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
                <Link
                  href={`mailto:${user.email}`}
                  className="flex w-fit items-center space-x-2 text-gray-600 decoration-dotted hover:underline hover:underline-offset-2 dark:text-gray-400"
                >
                  <FontAwesomeIcon icon={faEnvelope} className="text-sm" />
                  <span>{user.email}</span>
                </Link>
              )}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4 bg-gray-200 p-6 dark:bg-gray-900 sm:grid-cols-3">
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
            Joined {formatDate(user.created_at)}
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserDetailsPage
