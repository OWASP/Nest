'use client'

import { useQuery } from '@apollo/client/react'
import { useMemo } from 'react'
import {
  GetProjectCategoriesDocument,
  GetProjectCategoriesQuery,
} from 'types/__generated__/categoryQueries.generated'

type ProjectCategoryNode = GetProjectCategoriesQuery['projectCategories'][number]

export interface ProjectCategoryOption {
  id: string
  name: string
  slug: string
  description: string
  level: number
  fullPath: string
  isActive: boolean
}

export interface UseProjectCategoriesReturn {
  categories: ProjectCategoryOption[]
  isLoading: boolean
  error: Error | null
}

export function useProjectCategories(): UseProjectCategoriesReturn {
  const { data, loading, error } = useQuery(GetProjectCategoriesDocument, {
    variables: {
      offset: 0,
      limit: 1000,
    },
    errorPolicy: 'all',
  })

  const categories = useMemo(() => {
    if (!data?.projectCategories) return []

    return data.projectCategories.map((cat: ProjectCategoryNode) => ({
      id: cat.id,
      name: cat.name,
      slug: cat.slug,
      description: cat.description,
      level: cat.level,
      fullPath: cat.fullPath,
      isActive: cat.isActive,
    }))
  }, [data])

  return {
    categories,
    isLoading: loading,
    error: error ? new Error(error.message) : null,
  }
}

export function formatCategoryOptions(
  categories: ProjectCategoryOption[]
): Array<{ key: string; label: string }> {
  const options: Array<{ key: string; label: string }> = [{ key: '', label: 'All Categories' }]

  const sortedCategories = [...categories]
    .filter((cat) => cat.isActive)
    .sort((a, b) => {
      if (a.level !== b.level) return a.level - b.level
      return a.name.localeCompare(b.name)
    })

  sortedCategories.forEach((category) => {
    let prefix = ''
    if (category.level === 2) {
      prefix = '  • '
    } else if (category.level === 3) {
      prefix = '    • '
    }

    options.push({
      key: category.slug,
      label: `${prefix}${category.name}`,
    })
  })

  return options
}
