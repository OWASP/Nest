import { gql } from '@apollo/client'

export const GET_PROJECT_CATEGORIES = gql`
  query GetProjectCategories($offset: Int, $limit: Int) {
    projectCategories(pagination: { offset: $offset, limit: $limit }) {
      id
      name
      slug
      description
      level
      fullPath
      isActive
      parent {
        id
        name
        slug
      }
      children {
        id
        name
        slug
      }
    }
  }
`
