'use client'

import { useQuery, ApolloError } from '@apollo/client/react'
import { useMemo } from 'react'
import { GET_PROJECTS_LIST } from 'server/queries/projectQueries'
import { ProjectLevel, ProjectType } from 'types/__generated__/graphql'
import type { Project } from 'types/project'

interface UseSearchProjectsGraphQLOptions {
  pageSize?: number
}

interface UseSearchProjectsGraphQLReturn {
  items: Project[]
  isLoaded: boolean
  totalCount: number
  error: ApolloError | undefined
}

interface ProjectFilterInput {
  type?: ProjectType
  level?: ProjectLevel
  isActive?: boolean
}

interface ProjectOrderInput {
  [key: string]: 'ASC' | 'DESC'
}

/**
 * Hook to search projects using GraphQL backend with filtering, ordering, and pagination
 */
export function useSearchProjectsGraphQL(
  searchQuery = '',
  category = '',
  sortBy = '',
  order = '',
  currentPage = 1,
  pageSize = 25,
  _options?: UseSearchProjectsGraphQLOptions
): UseSearchProjectsGraphQLReturn {
  const filters = useMemo<ProjectFilterInput | undefined>(() => {
    const newFilters: ProjectFilterInput = {}

    if (category && category !== '' && category !== 'idx_type:') {
      const typeMatch = category.match(/idx_type:(\w+)/i)
      if (typeMatch) {
        const typeValue = typeMatch[1].toUpperCase()
        if (['CODE', 'TOOL', 'DOCUMENTATION', 'OTHER'].includes(typeValue)) {
          newFilters.type = typeValue as ProjectType
        }
      }
    }

    return Object.keys(newFilters).length > 0 ? newFilters : undefined
  }, [category])

  const ordering = useMemo<ProjectOrderInput[] | undefined>(() => {
    if (sortBy && sortBy !== 'default' && sortBy !== '') {
      const orderDirection = order === 'asc' ? 'ASC' : 'DESC'

      const fieldMapping = Object.fromEntries([
        ['contributors_count', 'contributorsCount'],
        ['forks_count', 'forksCount'],
        ['stars_count', 'starsCount'],
        ['updated_at', 'updatedAt'],
        ['created_at', 'createdAt'],
        ['level', 'level'],
        ['name', 'name'],
        ['default', ''],
      ])

      const graphQLField = fieldMapping[sortBy] || sortBy
      if (graphQLField) {
        return [{ [graphQLField]: orderDirection }]
      }
    }
    return undefined
  }, [sortBy, order])

  const offset = (currentPage - 1) * pageSize

  const searchParam = searchQuery.trim().length >= 3 ? searchQuery.trim() : ''

  const { data, loading, error } = useQuery(GET_PROJECTS_LIST, {
    variables: {
      query: searchParam || '', // Pass empty string if query is too short
      filters: Object.keys(filters || {}).length > 0 ? filters : undefined,
      ordering: ordering && ordering.length > 0 ? ordering : undefined,
      pagination: {
        offset,
        limit: pageSize,
      },
    },
    errorPolicy: 'all',
  })

  const projects = data?.searchProjects || []
  const totalProjects = data?.projectsTotal?.length || 0

  return {
    items: projects as Project[],
    isLoaded: !loading,
    totalCount: totalProjects,
    error,
  }
}
