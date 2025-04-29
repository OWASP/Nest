'use client'

import { useQuery } from '@apollo/client'
import { faChevronRight } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Breadcrumbs, BreadcrumbItem } from '@heroui/react'
import Link from 'next/link'
import { usePathname, useParams } from 'next/navigation'
import { useState, useEffect } from 'react'
import { GET_PROJECT_DATA } from 'server/queries/projectQueries'
import { GET_USER_DATA } from 'server/queries/userQueries'
import { ProjectTypeGraphql } from 'types/project'
import type { UserDetailsProps } from 'types/user'
import { capitalize } from 'utils/capitalize'

export default function BreadCrumbs() {
  const homeRoute = '/'
  const pathname = usePathname()
  const params = useParams()
  const memberKey = params?.memberKey
  const projectKey = params?.projectKey
  const segments = pathname?.split(homeRoute).filter(Boolean) || []
  const [user, setUser] = useState<UserDetailsProps | null>(null)
  const [project, setProject] = useState<ProjectTypeGraphql | null>(null)

  const { data: userData } = useQuery(GET_USER_DATA, {
    variables: { key: memberKey },
    skip: !memberKey,
  })

  const { data: projectData } = useQuery(GET_PROJECT_DATA, {
    variables: { key: projectKey },
    skip: !projectKey,
  })

  useEffect(() => {
    if (userData) {
      setUser(userData.user)
    }
  }, [userData])

  useEffect(() => {
    if (projectData) {
      setProject(projectData.project)
    }
  }, [projectData])

  if (pathname === homeRoute) return null

  return (
    <div className="mt-16 w-full pt-4">
      <div className="w-full px-8 sm:px-8 md:px-8 lg:px-8">
        <Breadcrumbs
          aria-label="breadcrumb"
          separator={
            <FontAwesomeIcon
              icon={faChevronRight}
              className="mx-1 text-xs text-gray-400 dark:text-gray-500"
            />
          }
          className="text-gray-800 dark:text-gray-200"
          itemClasses={{
            base: 'transition-colors duration-200',
            item: 'text-sm font-medium',
            separator: 'flex items-center',
          }}
        >
          <BreadcrumbItem>
            <Link
              href={homeRoute}
              className="hover:text-blue-700 hover:underline dark:text-blue-400"
            >
              Home
            </Link>
          </BreadcrumbItem>

          {segments.map((segment, index) => {
            const href = homeRoute + segments.slice(0, index + 1).join(homeRoute)
            const isLast = index === segments.length - 1
            const isAfterMember = index > 0 && segments[index - 1] === 'members'
            const isAfterProject = index > 0 && segments[index - 1] === 'projects'

            let label: string
            if (isAfterMember && user?.name) {
              label = user.name
            } else if (isAfterProject && project?.name) {
              label = project.name
            } else {
              label = capitalize(segment).replace(/-/g, ' ')
            }

            return (
              <BreadcrumbItem key={href} isDisabled={isLast}>
                {isLast ? (
                  <span className="cursor-default font-semibold text-gray-600 dark:text-gray-300">
                    {label}
                  </span>
                ) : (
                  <Link
                    href={href}
                    className="hover:text-blue-700 hover:underline dark:text-blue-400"
                  >
                    {label}
                  </Link>
                )}
              </BreadcrumbItem>
            )
          })}
        </Breadcrumbs>
      </div>
    </div>
  )
}
