'use client'

import { useQuery } from '@apollo/client/react'
import { useMemo } from 'react'
import { ProjectType } from 'types/__generated__/graphql'
import { GetProjectsListDocument } from 'types/__generated__/projectQueries.generated'
import type { Project } from 'types/project'

interface UseSearchProjectsGraphQLOptions {
  enabled?: boolean
}

interface UseSearchProjectsGraphQLReturn {
  items: Project[]
  isLoaded: boolean
  totalCount: number
  error: Error | undefined
}

function mapCategoryToProjectType(category: string): ProjectType | undefined {
  const typeMatch = /idx_type:(\w+)/i.exec(category)
  if (!typeMatch) return undefined

  const typeMap: Record<string, ProjectType> = {
    code: ProjectType.Code,
    tool: ProjectType.Tool,
    documentation: ProjectType.Documentation,
    other: ProjectType.Other,
  }
  return typeMap[typeMatch[1].toLowerCase()]
}

function buildGraphQLOrdering(
  sortBy: string,
  order: string
): Record<string, 'ASC' | 'DESC'>[] | undefined {
  if (!sortBy || sortBy === 'default') return undefined

  const fieldMap = new Map<string, string>([
    ['contributors_count', 'contributorsCount'],
    ['forks_count', 'forksCount'],
    ['stars_count', 'starsCount'],
    ['updated_at', 'updatedAt'],
    ['created_at', 'createdAt'],
    ['level_raw', 'level'],
    ['level', 'level'],
    ['name', 'name'],
  ])

  const graphQLField = fieldMap.get(sortBy)
  if (!graphQLField) return undefined

  const direction = order === 'asc' ? 'ASC' : 'DESC'
  const primaryOrdering = { [graphQLField]: direction } as Record<string, 'ASC' | 'DESC'>

  if (graphQLField !== 'name') {
    return [primaryOrdering, { name: 'ASC' as const }]
  }
  return [primaryOrdering]
}

export function useSearchProjectsGraphQL(
  searchQuery = '',
  category = '',
  sortBy = '',
  order = '',
  currentPage = 1,
  pageSize = 25,
  options?: UseSearchProjectsGraphQLOptions
): UseSearchProjectsGraphQLReturn {
  const filters = useMemo(() => {
    if (!category || category === '') return undefined
    const projectType = mapCategoryToProjectType(category)
    return projectType ? { type: projectType } : undefined
  }, [category])

  const ordering = useMemo(() => buildGraphQLOrdering(sortBy, order), [sortBy, order])

  const offset = (currentPage - 1) * pageSize
  const searchParam = searchQuery.trim()

  const { data, loading, error } = useQuery(GetProjectsListDocument, {
    variables: {
      query: searchParam,
      filters: filters ?? undefined,
      ordering: ordering ?? undefined,
      pagination: { offset, limit: pageSize },
    },
    errorPolicy: 'all',
    skip: options?.enabled === false,
  })

  const projects = data?.searchProjects || []
  const totalProjects = data?.projectsTotal || 0

  return {
    items: projects as Project[],
    isLoaded: !loading,
    totalCount: totalProjects,
    error,
  }
}
