import { gql } from '@apollo/client'

export const GET_USER_DATA = gql`
  query GetUser($key: String!) {
    user(login: $key) {
      avatarUrl
      bio
      company
      createdAt
      email
      followersCount
      followingCount
      key
      location
      login
      name
      publicRepositoriesCount
      title
      updatedAt
      url
    }
  }
`
